import asyncio

from services.orchestration.classifier import QueryClassifier


async def main():

    classifier = QueryClassifier()

    available_departments = [
        "IT",
        "HR",
        "Finance",
        "Facilities",
        "Administration",
    ]

    test_messages = [
        "My laptop is not connecting to campus WiFi.",
        "How many vacation days do I have?",
        "My fee payment failed.",
        "The AC in my classroom is not working.",
        "My laptop is broken and I also want to know my leave balance.",
        "Help me.",
    ]

    for message in test_messages:

        result = await classifier.classify(
            message=message,
            available_departments=available_departments,
        )

        print("\n" + "=" * 60)
        print("MESSAGE:", message)
        print("TOPICS:", result.topics)
        print("DEPARTMENTS:", result.departments)
        print("CONFIDENCE:", result.confidence)
        print("CLARIFICATION:", result.needs_clarification)


if __name__ == "__main__":
    asyncio.run(main())