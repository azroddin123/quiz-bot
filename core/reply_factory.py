
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question in Django session.
    """
    if current_question_id is None:
        return False, "No current question to answer."

    question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = question["answer"]

    # Validate the answer
    if answer not in question["options"]:
        return False, "Invalid answer. Please choose a valid option."

    # Store the answer in session
    session_answers = session.get("answers", [])
    session_answers.append({
        "question_id": current_question_id,
        "user_answer": answer,
        "is_correct": answer == correct_answer
    })
    session["answers"] = session_answers
    session.save()

    return True, ""



def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST.
    """
    if current_question_id is None:
        # Start with the first question
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    # Check if there are more questions
    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        return next_question, next_question_id
    else:
        # No more questions
        return None, None


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers.
    """
    session_answers = session.get("answers", [])
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for answer in session_answers if answer["is_correct"])

    # Build a summary
    summary = "\n".join(
        f"Q{answer['question_id'] + 1}: {'Correct' if answer['is_correct'] else 'Wrong'} (Your Answer: {answer['user_answer']})"
        for answer in session_answers
    )

    result_message = (
        f"Quiz Completed!\n"
        f"Your Score: {correct_answers}/{total_questions}\n\n"
        f"Summary:\n{summary}"
    )

    return result_message

