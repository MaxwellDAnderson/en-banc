import re
import json
import os

f = open("f2d_eb_full_9_final.json", "a", encoding="utf8")
f.write("[")
i = 1941

while i < 1994:
    read_path = "f2d_{}.json"
    working = "Examining cases for the year {}..."
    working_format = working.format(i)
    print(working_format)
    read_file = read_path.format(i)
    read = open(read_file, "r", encoding="utf8")
    json_file = json.load(read)

    for case in json_file:
        case_id = str(case['id'])
        name = case['name_abbreviation']
        volume = case['volume']['volume_number']
        reporter = "F.2d"
        first_page = case['first_page']
        cite = case['citations'][0]['cite']
        date = case['decision_date']
        year = date[0:4]
        court = case['court']['name_abbreviation']
        judges = case['casebody']['data']['judges']
        head_matter = case['casebody']['data']['head_matter']

        if court == "C.C.P.A." and "Ct. Cl.":
            continue

        # BEFORE PRE-CHECK
        if re.search("[Bb][Ee][Ff][Oo][Rr][Ee]", head_matter) is None:
            continue

        # SKIP IF ANY JUDGE IS SITTING BY DESIGNATION
        if len(re.findall("sitting by designation", head_matter)) > 0:
            continue

        if len(re.findall("[Aa]ssociate [Jj]ustice", head_matter)) > 0:
            continue

        start = re.search("[B][Ee][Ff][Oo][Rr][Ee]|[Bb][Ee][Ff][Oo][Rr][Ee]:|[Bb][Ee][Ff][Oo][Rr][Ee];|Present:", head_matter)
        end = re.search(r"Circuit Judges|Circuit Judge.|Circuit Judges.|Chief Judges.", head_matter)

        try:
            x = start.start()
        except AttributeError:
            pass

        try:
            y = end.end()
        except AttributeError:
            pass

        z = head_matter[x:y].strip()


        # COMMA REMOVER
        # Removing Comma Sandwiches
        rem_cj_comma = re.sub(", [Cc]hief [Jj]udge,", ",", z)
        rem_cir_j_comma = re.sub(", [Cc]ircuit [Jj]udge,", ",", rem_cj_comma)
        rem_cir_js_comma = re.sub(r", [Cc]ircuit [Jj]udges,", ",", rem_cir_j_comma)
        rem_sr_cir_j_comma = re.sub(", [Ss]enior [Cc]ircuit [Jj]udge,|,[Ss]enior [Cc]ircuit [Jj]udge,|,[Ss]enior [Cc]ircuit [Jj]udge.|, [Ss]enior [Jjudge],", ",", rem_cir_js_comma)
        rem_sr_cir_js_comma = re.sub(", [Ss]enior [Cc]ircuit [Jj]udges,", ",", rem_sr_cir_j_comma)

        rem_chief_comma = re.sub(", [Cc]hief [Jj]ustice,", ",", rem_sr_cir_js_comma)
        rem_assoc_comma = re.sub(", [Aa]ssociate [Jj]ustices,|, [Aa]ssociate [Jj]ustices.", ",", rem_chief_comma)

        rem_jr_comma = re.sub(r", [Jj][Rr].,", ",", rem_assoc_comma)
        rem_ii_comma = re.sub(", II,", ",", rem_jr_comma)
        rem_iii_comma = re.sub(", III,", ",", rem_ii_comma)
        rem_iv_comma = re.sub(", IV,", ",", rem_iii_comma)
        rem_v_comma = re.sub(", V,", ",", rem_iv_comma)

        rem_comma_space_comma = re.sub(" , ", ",", rem_v_comma)
        rem_double_comma = re.sub(",,|, ,", ",", rem_comma_space_comma)

        rem_initial = re.sub(r"[A-Z]+ [A-Z].", "", rem_double_comma)
        rem_initials = re.sub(r"[A-Z]+ [A-Z].[A-Z].", "", rem_initial)

        panel = re.sub(r"\s{2,}", " ", rem_double_comma)

        dj_find = re.findall("[Dd]istrict [Jj]udge", panel)
        if len(dj_find) > 0:
            continue

        sit_by_desig_find = re.findall("sitting by designation", panel)
        if len(sit_by_desig_find) > 0:
            continue

        one_all_caps = re.findall("[A-Z][A-Z]+", panel)
        if len(one_all_caps) == 0:
            continue

        comma_find = re.findall(",", panel)
        no_ox_comma = re.findall("[A-Z]+ and [A-Z]+", panel)

        if len(no_ox_comma) > 0:
            len(comma_find) + 1

        eb_dict = {
            "id": case_id,
            "date": date,
            "court": court,
            "name": name,
            "cite": cite,
            "vol": volume,
            "reporter": reporter,
            "first_page": first_page,
            "clean_panel": panel,
            "judges": judges,
            "head_matter": head_matter
        }

        serial = json.dumps(eb_dict, indent=4, separators=(", ", ": ")) + ", "

        if len(comma_find) > 3:
            f.write(serial)

    i += 1

f.seek(f.tell() - 2, os.SEEK_SET)
f.truncate()
f.write("]")
f.close()
