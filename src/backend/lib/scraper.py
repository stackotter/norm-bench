import requests
from typing import Tuple

def get_letters_and_words() -> Tuple[list[str], list[str]]:
    create_room = {
        "operationName": "CREATE_ROOM",
        "variables": {
            "name": "normbench"
        },
        "query": """mutation CREATE_ROOM($name: String!) {
            createRoom(name: $name) {
                id
                stage
                players {
                    id
                    name
                    completedWords
                    __typename
                }
                __typename
            }
        }"""
    }

    query_room = {
        "operationName": "FETCH_ROOM",
        "variables": {
            "roomId":"5761"
        },
        "query": """query FETCH_ROOM($roomId: ID!) {
            room(roomId: $roomId) {
                id
                stage
                players {
                    id
                    name
                    completedWords
                    __typename
                }
                board {
                    height
                    width
                    letters
                    words {
                        word
                        startLocation {
                            rowNum
                            colNum
                            __typename
                        }
                        direction
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        """
    }

    # Create a new word-bench room
    response = requests.post("https://word-bench.herokuapp.com/graphql", headers={"X-User-Id": "de451951-7b63-4242-83eb-d8e01675a607"}, json=create_room)
    room_id = response.json()["data"]["createRoom"]["id"]
    query_room["variables"]["roomId"] = room_id # type: ignore

    # Fetch the letters and words
    response = requests.post("https://word-bench.herokuapp.com/graphql", headers={"X-User-Id": "de451951-7b63-4242-83eb-d8e01675a607"}, json=query_room)
    room_data = response.json()
    board = room_data["data"]["room"]["board"]
    letters = board["letters"]
    words = [elem["word"] for elem in board["words"]]

    return (letters, words)
