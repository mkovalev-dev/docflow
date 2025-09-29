def collect_party_ids(docs):
    users, ext_users, orgs = set(), set(), set()

    for d in docs:
        # Исполнитель
        users.add(str(d.creator_id))

        # регистрация
        reg = getattr(d, "registration", None)
        if reg:
            regnum = getattr(reg, "registration_number", None)
            if regnum and regnum.registrator:
                users.add(str(regnum.registrator))

        # адресация
        for ap in getattr(d, "address_parties", []) or []:
            if ap.user_id:
                users.add(str(ap.user_id))
            if ap.external_user_id:
                ext_users.add(str(ap.external_user_id))
            if ap.organization_id:
                orgs.add(str(ap.organization_id))

    return users, ext_users, orgs
