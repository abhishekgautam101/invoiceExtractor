"""
This module abstracts templates for invoice providers.

Templates are initially read from .yml files and then kept as class.
"""

import re
import dateparser
from unidecode import unidecode
import logging
from collections import OrderedDict
from .plugins import lines, tables

logger = logging.getLogger(__name__)

OPTIONS_DEFAULT = {
    "remove_whitespace": False,
    "remove_accents": False,
    "lowercase": False,
    "currency": "EUR",
    "date_formats": [],
    "languages": [],
    "decimal_separator": ".",
    "replace": [],  # example: see templates/fr/fr.free.mobile.yml
}

PLUGIN_MAPPING = {"lines": lines, "tables": tables}


class InvoiceTemplate(OrderedDict):
    """
    Represents single template files that live as .yml files on the disk.

    Methods
    -------
    prepare_input(extracted_str)
        Input raw string and do transformations, as set in template file.
    matches_input(optimized_str)
        See if string matches keywords set in template file
    parse_number(value)
        Parse number, remove decimal separator and add other options
    parse_date(value)
        Parses date and returns date after parsing
    coerce_type(value, target_type)
        change type of values
    extract(optimized_str)
        Given a template file and a string, extract matching data fields.
    """

    def __init__(self, *args, **kwargs):
        super(InvoiceTemplate, self).__init__(*args, **kwargs)

        # Merge template-specific options with defaults
        self.options = OPTIONS_DEFAULT.copy()

        for lang in self.options["languages"]:
            assert len(lang) == 2, "lang code must have 2 letters"

        if "options" in self:
            self.options.update(self["options"])

    def prepare_input(self, extracted_str):
        """
        Input raw string and do transformations, as set in template file.
        """

        # Remove withspace
        if self.options["remove_whitespace"]:
            optimized_str = re.sub(" +", "", extracted_str)
        else:
            optimized_str = extracted_str

        # Remove accents
        if self.options["remove_accents"]:
            optimized_str = unidecode(optimized_str)

        # convert to lower case
        if self.options["lowercase"]:
            optimized_str = optimized_str.lower()

        # specific replace
        for replace in self.options["replace"]:
            assert len(replace) == 2, "A replace should be a list of 2 items"
            optimized_str = optimized_str.replace(replace[0], replace[1])

        return optimized_str

    def matches_input(self, optimized_str):
        """See if string matches keywords set in template file and keywords order is correct"""
        # keywords_positions = self.get_kewords_positions(optimized_str) 
        # if keywords_positions and self.keywords_ordered(list(keywords_positions.values())):
        #     logger.debug("Matched template %s", self["template_name"])
        #     return True
        return True
    
    def get_kewords_positions(self, optimized_str):
        """Get positions of keywords in pdf invoice"""
        keywords_positions = OrderedDict()
        for keyword in self['keywords']:
            if keyword not in optimized_str:
                logger.debug("Keyword %s not found", keyword)
                return False
            keywords_positions[keyword] = re.search(keyword, optimized_str).start()
        logger.debug("Keywords-positions ordered dict created")
        return keywords_positions

    def keywords_ordered(self, keywords_values):
        """Check if order of keywords is correct in an invoice"""
        result = all(keywords_values[i] <= keywords_values[i+1] for i in range(len(keywords_values)-1))
        return result

    def parse_number(self, value):
        assert (
            value.count(self.options["decimal_separator"]) < 2
        ), "Decimal separator cannot be present several times"
        # replace decimal separator by a |
        amount_pipe = value[1].replace(self.options["decimal_separator"], "|")
        # remove all possible thousands separators
        amount_pipe_no_thousand_sep = re.sub(r"[.,\s]", "", amount_pipe)
        # put dot as decimal sep
        return float(amount_pipe_no_thousand_sep.replace("|", "."))

    def parse_date(self, value):
        """Parses date and returns date after parsing"""
        res = dateparser.parse(
            value,
            date_formats=self.options["date_formats"],
            languages=self.options["languages"],
        )
        logger.debug("result of date parsing=%s", res)
        return res

    def coerce_type(self, value, target_type):
        if target_type == "int":
            if not value.strip():
                return 0
            return int(self.parse_number(value))
        elif target_type == "float":
            if not value.strip():
                return 0.0
            return float(self.parse_number(value))
        elif target_type == "date":
            print(value)
            return self.parse_date(value)
        assert False, "Unknown type"

    def extract(self, optimized_str):
        """
        Given a template file and a string, extract matching data fields.
        """

        logger.debug("START optimized_str ========================")
        logger.debug(optimized_str)
        logger.debug("END optimized_str ==========================")
        logger.debug(
            "Date parsing: languages=%s date_formats=%s",
            self.options["languages"],
            self.options["date_formats"],
        )
        logger.debug(
            "Float parsing: decimal separator=%s", self.options["decimal_separator"]
        )
        logger.debug("keywords=%s", self["keywords"])
        logger.debug(self.options)

        # Try to find data for each field.
        output = {}
        
        for k, v in self["fields"].items():  
            if k.startswith("static_"):
                logger.debug("field=%s | static value=%s", k, v)
                output[k.replace("static_", "")] = v
            else:
                logger.debug("field=%s | regexp=%s", k, v)

                sum_field = False
                if k.startswith("sum_amount") and type(v) is list:
                    k = k[4:]  # remove 'sum_' prefix
                    sum_field = True
                # Fields can have multiple expressions
                if type(v) is list:
                    res_find = []
                    for v_option in v:
                        # extract date invoice published
                        if k.startswith("date") or k.endswith("date"):
                            regexpt = re.search(v_option, optimized_str)
                            if regexpt and regexpt.group(1) is not None:
                                output[k] = regexpt.group(1)
                        else:
                            res_val = re.findall(v_option, optimized_str)
                            if res_val:
                                if sum_field:
                                    res_find += res_val
                                else:
                                    res_find.extend(res_val)
                    # check if date is set if not log error
                    if not output['date']:
                        logger.error("Date parsing failed on date '%s'", res_find[0])
                        return None
                else:
                    if k in ['issuer', 'purchaser']:
                        output[k] = re.search(v, optimized_str).group(2)
                    else:
                        res_find = re.findall(v, optimized_str)
                        
                        if res_find:
                            logger.debug("res_find=%s", res_find)
                            if k.startswith("amount"):
                                if sum_field:
                                    output[k] = 0
                                    for amount_to_parse in res_find:
                                        output[k] += self.parse_number(amount_to_parse)
                                else:
                                    output[k] = self.parse_number(res_find[0])
                            else:
                                res_find = list(set(res_find))
                                if len(res_find) == 1:
                                    output[k] = res_find[0]
                                else:
                                    output[k] = res_find
                        else:
                            logger.warning("regexp for field %s didn't match", k)

        output["currency"] = self.options["currency"]
        
        # Run plugins:
        for plugin_keyword, plugin_func in PLUGIN_MAPPING.items():
            if plugin_keyword in self.keys():
                plugin_func.extract(self, optimized_str, output)
        
        # If required fields were found, return output, else log error.
        if "required_fields" not in self.keys():
            required_fields = ["purchaser", "issuer"]
        else:
            required_fields = []
            for v in self["required_fields"]:
                required_fields.append(v)
        
        if set(required_fields).issubset(output.keys()):
            output["desc"] = "Invoice extracted using template with keywords: %s" % (', '.join(self["keywords"]))
            logger.debug(output)
            return output
        else:
            fields = list(set(output.keys()))
            logger.error(
                "Unable to match all required fields. "
                "The required fields are: {0}. "
                "Output contains the following fields: {1}.".format(
                    required_fields, fields
                )
            )
            return None
