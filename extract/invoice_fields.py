import re, math

measure_units = ['m', 'opak.', 'opak', 'szt.', 'szt', 'kg', 'l', 'zł', 'zl', 'PLN']
lp_regexp = '^([0-9\.]*).*$'
reg='(\d{0,1}.{0,1})\s*([a-zA-Ząćńłźżś\d ]{0,})'
desc_regexp = '([a-zA-ZŁ ])'
tax_regexp = "(\d{1,3}[.,]*\d{0,3})\s*%"
amount_regexp = "(\d{1,}[.,]*\d{0,2})"
splitter_regexp = '\d*\s*\d{1,}[.,]*\d{0,2}(\s+\d{1,}%)'
# Each invoice should have at least 5 fields (description, amount, net value, tax, gross value)
# if not other table than with lines may be extracted
MIN_FIELS_NUM = 5

# class InvoiceFields():
#     def __init__(self, extractedData):
#         self.extractedData = extractedData
#         self.lines = extractedData['lines'][0]['pos'].split('\n')
#         self.header = []
#         self.fields_order = {}
        

#     def clear_invoice_lines(self):
#         splitted_lines = [re.split('\s{2,}', line) for line in self.lines]
#         self.header = splitted_lines.pop(0)
#         cleared_lines = []
#         for line in splitted_lines:
#             separate_fields(line)
#             if len(line) > MIN_FIELS_NUM:
#                 cleared_lines.append(line)
#         self.lines = cleared_lines


#     def separate_fields(self, line):
#         for field in line:
#             if re.search(splitter_regexp, field):
#                 line.append(field.split(re.search(splitter_regexp, field).group(1)).pop(0))
#                 line.append(re.search(splitter_regexp, field).group(1).replace(' ', ''))
#                 line.remove(field)
    
#     def validate_float_value(self, field):
#         return float(re.sub('[A-Za-zł\s+]', '', field).replace(',', '.'))

#     def get_indexed_data(self, line):
#         qty = self.validate_float_value(line[self.fields_order['qty']])
#         discount, PKWiU = '', ''
#         elems = [line[self.fields_order['qty']]]

#         if 'PKWiU' in self.fields_order.keys():
#             PKWiU = re.search('\s*(\d{1,3}\.*\d{0,3}\.*\d{0,3})\s*', line[self.fields_order['PKWiU']]).group(1)
#             elems.append(line[self.fields_order['PKWiU']])
#         if 'discount' in self.fields_order.keys():
#             nums = re.search('\s*([0-9]{1,}[.,]*\d{0,2})\s*%*\s*', line[self.fields_order['discount']]).group(1)
#             discount = validate_float_value(nums)/100
#             elems.append(line[self.fields_order['discount']])
#         for elem in elems:
#             line.remove(elem)
#         return qty, discount, PKWiU

#     def get_no_description(self, line):
#         reg1 = '^([0-9]{1,})[.,]{0,1}\s*([A-Za-z1-9ąćęńółźżśĄĆĘŁŃŚŹŻ\-\n\s]*)'
#         reg2 = '^([A-Za-z0-9ąćęńółźżśĄĆĘŁŃŚŹŻ\-\n\s]{1,})' 
#         line_no = ''

#         if re.search(reg1, line[0]):
#             groups = re.search(reg1, line[0]).groups()
#             line_no = groups[0]
#             if groups[1]:
#                 desc = groups[1]
#             else:
#                 desc = groups = re.search(reg2, line[1]).group(1)
#                 line.remove(line[1])
#             line.remove(line[0])
#         elif re.search(reg2, line[0]):
#             desc = groups = re.search(reg2, line[0]).group(1)
#             line.remove(line[0])
#         return line_no, desc


#     def get_measurement_unit(self, line):
#         for unit in measure_units:
#             for field in line:
#                 if unit in field or re.search(amount_regexp + '\s*{}'.format(unit), field):
#                     line.remove(field)
#                     return unit


#     def get_percentage_rate(self, line, check_tax=False):
#         for field in line:
#             if re.search(tax_regexp, field):
#                 tax = float(re.search(tax_regexp, field).group(1))
#                 if check_tax and tax in [23, 8, 7, 4, 0]:
#                         line.remove(re.search(tax_regexp, field).group(0))
#                         return tax/100
#                 else:
#                     line.remove(re.search(tax_regexp, field).group(0))
#                     return tax/100



#     def analize_heading(self):
#         qty = 'Ilość,ilość,ILOŚĆ,Ilosc,ilosc'
#         PKWiU = 'PKWiU'
#         discount = 'Rabat,rabat,Obnizka,% OBNIŻKI,obnizka,Obniżka,obniżka'
#         reg1 = '^([0-9]{1,})[.,]{0,1}\s*([A-Za-z1-9ąćęńółźżśĄĆĘŁŃŚŹŻ\-\n\s]{1,})'

#         for counter, value in enumerate(self.header):
#             if value in qty.split(','):
#                 self.fields_order['qty'] = counter
#             if value in discount.split(','):
#                 self.fields_order['discount'] = counter
#             elif value in PKWiU:
#                 self.fields_order['PKWiU'] = counter
#         # check if lp is separated from product name/description
#         # if not shift back field order
#         if re.search(reg1, self.lines[0][0]):
#             for key, value in fields_order.items():
#                 self.fields_order[key] = value -1

#     def analize_fields(self, line):
#         fields = {}
#         fields['qty'], fields['discount'], fields['PKWiU'] = self.get_indexed_data(line)
#         fields['line_no'], fields['description'] = self.get_no_description(line)
#         fields['unit'] = self.get_measurement_unit(line)
#         fields['tax_rate'] = self.get_percentage_rate(line, True)
#         # fields['gross_value'] = get_gross_value(line)
#         # fields['net_value'] = get_net_value(line, fields)
#         # remove_total_tax(line, fields)
#         # fields['unit_price'] = get_unit_price(line, fields['net_value'], fields['qty'])

#         return fields

#     def analize_data(self):
#         self.clear_invoice_lines()
#         self.extractedData['lines'] = []
#         self.fields_order = self.analize_heading()

#         for line in self.lines:
#             self.extractedData['lines'].append(self.analize_fields(line))

def clear_invoice_lines(lines):
    splitted_lines = [re.split('\s{2,}', line) for line in lines]
    heading = splitted_lines.pop(0)
    cleared_lines = []
    for line in splitted_lines:
        separate_fields(line)
        if len(line) > MIN_FIELS_NUM:
            cleared_lines.append(line)
    return heading, cleared_lines


def separate_fields(line):
    for field in line:
        if re.search(splitter_regexp, field):
            line.append(field.split(re.search(splitter_regexp, field).group(1)).pop(0))
            line.append(re.search(splitter_regexp, field).group(1).replace(' ', ''))
            line.remove(field)



def get_indexed_data(fields_order, line):
    qty = str(validate_float_value(line[fields_order['qty']]))
    discount, PKWiU = '', ''
    elems = [line[fields_order['qty']]]

    if 'PKWiU' in fields_order.keys():
        PKWiU = re.search('\s*(\d{1,3}\.*\d{0,3}\.*\d{0,3})\s*', line[fields_order['PKWiU']]).group(1)
        elems.append(line[fields_order['PKWiU']])
    if 'discount' in fields_order.keys():
        nums = re.search('\s*([0-9]{1,}[.,]*\d{0,2})\s*%*\s*', line[fields_order['discount']]).group(1)
        discount = str(validate_float_value(nums)/100)
        elems.append(line[fields_order['discount']])
    for elem in elems:
        line.remove(elem)
    return qty, discount, PKWiU

def get_no_description(line):
    reg1 = '^([0-9]{1,})[.,]{0,1}\s*([A-Za-z0-9ąćęńółźżśĄĆĘŁŃŚŹŻ,.\-\n\s]*)'
    reg2 = '^([A-Za-z0-9ąćęńółźżśĄĆĘŁŃŚŹŻ,.\-\n\s]{1,})' 
    line_no = ''

    if re.search(reg1, line[0]):
        groups = re.search(reg1, line[0]).groups()
        line_no = groups[0]
        if groups[1]:
            desc = groups[1]
        else:
            desc = groups = re.search(reg2, line[1]).group(1)
            line.remove(line[1])
        line.remove(line[0])
    elif re.search(reg2, line[0]):
        desc = groups = re.search(reg2, line[0]).group(1)
        line.remove(line[0])
    return line_no, desc


def get_measurement_unit(line):
    for unit in measure_units:
        for field in line:
            if unit in field or re.search(amount_regexp + '\s*{}'.format(unit), field):
                line.remove(field)
                return unit


def get_percentage_rate(line, check_tax=False):
    for field in line:
        if re.search(tax_regexp, field):
            tax = float(re.search(tax_regexp, field).group(1))
            if check_tax and tax in [23, 8, 7, 4, 0]:
                    line.remove(re.search(tax_regexp, field).group(0))
                    return str(tax/100)
            else:
                line.remove(re.search(tax_regexp, field).group(0))
                return str(tax/100)


def validate_float_value(field):
    return float(re.sub('[A-Za-zł%\s+]', '', field).replace(',', '.'))


def get_gross_value(line):
    amounts = [validate_float_value(field) for field in line]
    field_to_remove = ''
    gross_value = max(amounts)
    for field in line:
        if gross_value == validate_float_value(field):
            field_to_remove = field
    line.remove(field_to_remove)
    return str(gross_value)

def get_unit_price(line, net_value, qty):
    unit_price, trash = '', ''
    unit_price = round(float(net_value)/float(qty), 2)
    return str(unit_price)
    

def get_net_value(line, fields):
    gross_value = float(fields['gross_value'])
    net_value = round(gross_value / (1 + float(fields['tax_rate'])), 2)
    for field in line:
        if net_value == validate_float_value(field):
            line.remove(field)
    return str(net_value)


def remove_total_tax(line, fields):
    if fields['discount']:
        total_tax = round(float(fields['tax_rate']) * ((1 - float(fields['discount'])) * float(fields['net_value'])), 2) 
    else:
        total_tax = round(float(fields['tax_rate']) * float(fields['net_value']), 2)
    for field in line:
        if total_tax == validate_float_value(field):
            line.remove(field)


def analize_heading(heading, line):
    qty = 'Ilość,ilość,ILOŚĆ,Ilosc,ilosc'
    PKWiU = 'PKWiU'
    discount = 'Rabat,rabat,Obnizka,% OBNIŻKI,obnizka,Obniżka,obniżka'
    reg1 = '^([0-9]{1,})[.,]{0,1}\s*([A-Za-z1-9ąćęńółźżśĄĆĘŁŃŚŹŻ\-\n\s]{1,})'

    fields_order = {}
    for counter, value in enumerate(heading):
        if value in qty.split(','):
            fields_order['qty'] = counter
        if value in discount.split(','):
            fields_order['discount'] = counter
        elif value in PKWiU:
            fields_order['PKWiU'] = counter
    # check if lp is separated from product name/description
    # if not shift back field order
    if re.search(reg1, line[0]):
        for key, value in fields_order.items():
            fields_order[key] = value -1
    return fields_order


def analize_fields(fields_order, line):
    fields = {}
    fields['qty'], fields['discount'], fields['PKWiU'] = get_indexed_data(fields_order, line)
    fields['line_no'], fields['description'] = get_no_description(line)
    fields['unit'] = get_measurement_unit(line)
    fields['tax_rate'] = get_percentage_rate(line, True)
    fields['gross_value'] = get_gross_value(line)
    fields['net_value'] = get_net_value(line, fields)
    remove_total_tax(line, fields)
    fields['unit_price'] = get_unit_price(line, fields['net_value'], fields['qty'])

    return fields