def tags_to_qgs_parameter_matrix_string(tags: dict[str, str]) -> str:
    """Convert a tags dict to a QgsProcessingParameterMatrix str

    :param tags: tags dict
    :type tags: dict[str, str]
    :return: QgsProcessingParameterMatrix string
    :rtype: str
    """
    return ";".join(f"{k},{v}" for k, v in tags.items())


def tags_from_qgs_parameter_matrix_string(param_string: str) -> dict[str, str]:
    """Convert QgsProcessingParameterMatrix str to a tags dict

    :param param_string: QgsProcessingParameterMatrix string
    :type param_string: str
    :return: tags dict
    :rtype: dict[str, str]
    """
    tag_values = [param_string[i : i + 2] for i in range(0, len(param_string), 2)]
    tags = {key: value for key, value in tag_values if key}
    return tags
