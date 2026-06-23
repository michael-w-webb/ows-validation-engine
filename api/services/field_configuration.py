def field_is_configured(
    field: dict
):

    column_type = field.get(
        "column_type"
    )

    accepted_responses = field.get(
        "accepted_responses",
        []
    )

    if column_type is None:

        return False

    if (
        column_type == "categorical"
        and not accepted_responses
    ):

        return False

    return True