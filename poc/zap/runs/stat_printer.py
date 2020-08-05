import json

with open ("f761a414-a387-476e-b881-1fce4b7fe317.json", "r") as j_file:
    p_file = json.loads(j_file.read())
    found = len(p_file)
    
    info = len([elem for elem in p_file if elem["risk"] == "Informational"])
    low = len([elem for elem in p_file if elem["risk"] == "Low"])
    medium = len([elem for elem in p_file if elem["risk"] == "Medium"])
    high = len([elem for elem in p_file if elem["risk"] == "High"])

    alerts = []
    for alert in p_file:
        if (alert["alert"], alert["risk"]) not in alerts:
            alerts.append((alert["alert"], alert["risk"]))

    grouped_alerst_risk_info = len([elem for elem in alerts if elem[1] == "Informational"])
    grouped_alerst_risk_low = len([elem for elem in alerts if elem[1] == "Low"])
    grouped_alerst_risk_medium = len([elem for elem in alerts if elem[1] == "Medium"])
    grouped_alerst_risk_high = len([elem for elem in alerts if elem[1] == "High"])

    print(f"Amount Alerts: {found}")
    print(f"Amount Informational: {info}")
    print(f"Amount Low: {low}")
    print(f"Amount Medium: {medium}")
    print(f"Amount High: {high}")
    print(f"-------------------------------")
    print(f"Different alerts: {len(alerts)}")
    print(f"Amount Grouped Informational: {grouped_alerst_risk_info}")
    print(f"Amount Grouped Low: {grouped_alerst_risk_low}")
    print(f"Amount Grouped Medium: {grouped_alerst_risk_medium}")
    print(f"Amount Grouped High: {grouped_alerst_risk_high}")