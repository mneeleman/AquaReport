import xml.etree.ElementTree as ElT
import csv


def compare_qaperstagevsqapertopic(ar_file1):
    ar1_xml = _loadaquareport_(ar_file1)
    root = ar1_xml.getroot()
    el1 = root.findall('QaPerStage')[0]
    el2 = root.findall('QaPerTopic')[0]
    for c1 in el1:
        for d2 in el2.iter('Stage'):
            if d2.attrib['Number'] == c1.attrib['Number']:
                for d1, dd2 in zip(c1.iter(), d2.iter()):
                    print('True') if d1.attrib == dd2.attrib else print(d1.attrib, dd2.attrib)


def compare_aquareports(ar_file1, ar_file2, outfile='compare_aq.csv'):
    with open(outfile, 'w') as file:
        csvwriter = csv.writer(file)
        _projectstructure_(ar_file1, ar_file2, csvwriter)
        csvwriter.writerow('')
        _qasummary_(ar_file1, ar_file2, csvwriter)
        csvwriter.writerow('')
        _qastages_(ar_file1, ar_file2, csvwriter)
        csvwriter.writerow('')
        _qatopic_(ar_file1, ar_file2, csvwriter, sensitivities=False)
        csvwriter.writerow('')
        _qatopic_(ar_file1, ar_file2, csvwriter, flux_measurements=False)


def _loadaquareport_(file_name):
    with open(file_name) as file:
        return ElT.parse(file)


def _projectstructure_(ar_file1, ar_file2, csvwriter):
    ar1_xml, ar2_xml = _loadaquareport_(ar_file1), _loadaquareport_(ar_file2)
    columns, c1text, c2text = _compare_xml_children_text_(ar1_xml, ar2_xml, 'ProjectStructure')
    csvwriter.writerow(columns)
    csvwriter.writerow(c1text)
    csvwriter.writerow(c2text)


def _qasummary_(ar_file1, ar_file2, csvwriter):
    ar1_xml, ar2_xml = _loadaquareport_(ar_file1), _loadaquareport_(ar_file2)
    columns, c1text, c2text = _compare_xml_children_text_(ar1_xml, ar2_xml, 'QaSummary')
    csvwriter.writerow(columns)
    csvwriter.writerow(c1text)
    csvwriter.writerow(c2text)


def _qastages_(ar_file1, ar_file2, csvwriter):
    ar1_xml, ar2_xml = _loadaquareport_(ar_file1), _loadaquareport_(ar_file2)
    el1, el2 = ar1_xml.getroot().find('QaPerStage'), ar2_xml.getroot().find('QaPerStage')
    # take the longer list as the one that defines the stage columns
    longer_list = list(el1) if len(list(el1)) > len(list(el2)) else list(el2)
    columns1 = [x.attrib['Name'] for x in longer_list]
    columns1.insert(0, 'StageName')
    columns2 = [x.attrib['Number'] for x in longer_list]
    columns2.insert(0, 'StageNumber')
    c1score, cnt1, c2score, cnt2 = ['AR1'], 0, ['AR2'], 0
    for col1 in columns1[1:]:
        if list(el1)[cnt1].attrib['Name'] == col1:
            c1score.append(list(el1)[cnt1].find('RepresentativeScore').attrib['Score'])
            cnt1 += 1
        else:
            c1score.append('---')
        if list(el2)[cnt2].attrib['Name'] == col1:
            c2score.append(list(el2)[cnt2].find('RepresentativeScore').attrib['Score'])
            cnt2 += 1
        else:
            c2score.append('---')
    csvwriter.writerow(columns1)
    csvwriter.writerow(columns2)
    csvwriter.writerow(c1score)
    csvwriter.writerow(c2score)


def _qatopic_(ar_file1, ar_file2, csvwriter, flux_measurements=True, sensitivities=True):
    ar1_xml, ar2_xml = _loadaquareport_(ar_file1), _loadaquareport_(ar_file2)
    el1, el2 = ar1_xml.getroot().find('QaPerTopic'), ar2_xml.getroot().find('QaPerTopic')
    if flux_measurements:
        fm_col1, fm_col2, fm_c1, fm_c2 = ['FluxMeasurements'], [''], ['AR1'], ['AR2']
        for idx in [0, 2]:  # loop over data set and calibration fluxes
            fm_zip = zip(el1[idx].find('FluxMeasurements').findall('FluxMeasurement'),
                         el2[idx].find('FluxMeasurements').findall('FluxMeasurement'))
            for fm1, fm2 in fm_zip:
                fm_col1.append(fm1.attrib['Field'])
                fm_col1.append(fm1.attrib['MsSpwId'])
                fm_col2.append('FluxJy')
                fm_col2.append('FrequencyGHz')
                fm_c1.append(fm1.attrib['FluxJy'])
                fm_c1.append(fm1.attrib['FrequencyGHz'])
                fm_c2.append(fm2.attrib['FluxJy'])
                fm_c2.append(fm2.attrib['FrequencyGHz'])
        csvwriter.writerow(fm_col1)
        csvwriter.writerow(fm_col2)
        csvwriter.writerow(fm_c1)
        csvwriter.writerow(fm_c2)
    if sensitivities:
        se_col1, se_col2, se_c1, se_c2 = ['Sensitivities'], [''], ['AR1'], ['AR2']
        se_zip = zip(el1[0].find('SensitivityEstimates').findall('Sensitivity'),
                     el2[0].find('SensitivityEstimates').findall('Sensitivity'))
        for se1, se2 in se_zip:
            se_col1.append(se1.attrib['Field'] + ' for BWmode ' + se1.attrib['BwMode'])
            [se_col1.append('') for _x in range(3)]
            col_names = ['SensitivityJyPerBeam', 'BeamMajArcsec', 'BeamMinArcsec', 'BeamPosAngDeg']
            [se_col2.append(col_name) for col_name in col_names]
            [se_c1.append(se1.attrib[col_name]) for col_name in col_names]
            [se_c2.append(se2.attrib[col_name]) for col_name in col_names]
        csvwriter.writerow(se_col1)
        csvwriter.writerow(se_col2)
        csvwriter.writerow(se_c1)
        csvwriter.writerow(se_c2)


def _compare_xml_children_text_(xml1, xml2, element_name):
    el1, el2 = xml1.getroot().find(element_name), xml2.getroot().find(element_name)
    c1tag, c2tag = {x.tag for x in list(el1)}, {x.tag for x in list(el2)}
    columns = list(c1tag | c2tag)
    columns.insert(0, element_name)
    c1text, c2text = ['AR1'], ['AR2']
    for column in columns[1:]:
        try:
            c1text.append(el1.find(column).text)
        except AttributeError:
            c1text.append('---')
        try:
            c2text.append(el2.find(column).text)
        except AttributeError:
            c2text.append('---')
    return columns, c1text, c2text
