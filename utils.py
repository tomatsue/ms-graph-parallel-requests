def build_filters(property, borders):
    filter_template = '{0} ge {1} and {0} lt {1}'.format(property, "{}")

    filters = [f'{property} lt {borders[0]}']

    for i in range(len(borders)-1):
        filters.append(filter_template.format(borders[i], borders[i+1]))

    filters.append(f'{property} ge {borders[-1]}')

    return filters


def build_filters_upn(borders='abcdefghijklmnopqrstuvwxyz'):
    filter_template = "userPrincipalName ge '{}' and userPrincipalName le '{}'"

    filters = [f"userPrincipalName le '{borders[0]}'"]

    for i in range(len(borders)-1):
        filters.append(filter_template.format(borders[i], borders[i+1]))

    filters.append(f"userPrincipalName ge '{borders[-1]}'")

    return filters
