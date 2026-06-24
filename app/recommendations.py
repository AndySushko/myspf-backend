from app.schemas import RecommendationItem


def get_recommendations(
    uv: float,
    phototype: str
) -> list[RecommendationItem]:

    recommendations = []

    if uv < 2:
        return recommendations

    # SPF

    if phototype == "I-II":
        spf = "Используйте SPF 50+"
    elif phototype == "III":
        spf = "Используйте SPF 50"
    elif phototype == "IV":
        spf = "Используйте SPF 30-50"
    elif phototype == "V":
        spf = "Используйте SPF 30"
    else:
        spf = "Используйте SPF 15-30"

    recommendations.append(
        RecommendationItem(
            type="sunscreen",
            title=spf,
            icon="icon_sunscreen"
        )
    )

    # вода

    if uv >= 4:
        recommendations.append(
            RecommendationItem(
                type="water",
                title="Пейте достаточно воды",
                icon="icon_bottle_of_water"
            )
        )

    # головной убор

    if uv >= 5:
        recommendations.append(
            RecommendationItem(
                type="cap",
                title="Наденьте головной убор",
                icon="icon_cap"
            )
        )

    # очки

    if uv >= 3:

        cat = (
            "CAT 2"
            if uv < 5
            else "CAT 3"
            if uv < 8
            else "CAT 4"
        )

        recommendations.append(
            RecommendationItem(
                type="glasses",
                title=f"Используйте солнцезащитные очки {cat}",
                icon="icon_sunglasses"
            )
        )

    # экстремальный UV

    if phototype == "I-II" and uv >= 9:
        recommendations.append(
            RecommendationItem(
                type="house",
                title="По возможности не выходите сейчас на открытое солнце",
                icon="icon_house"
            )
        )

    elif phototype == "III" and uv >= 10:
        recommendations.append(
            RecommendationItem(
                type="house",
                title="По возможности не выходите сейчас на открытое солнце",
                icon="icon_house"
            )
        )

    return recommendations