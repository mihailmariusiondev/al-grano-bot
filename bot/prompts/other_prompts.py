# bot/prompts/other_prompts.py
from typing import Dict, Callable

# Placeholder for prompts related to other content types like polls or photos,
# if they were to be re-introduced or if new miscellaneous types are added.
# Currently, photo and poll functionalities are marked for removal, so their prompts are not included.

# Example (if photo prompt existed and was to be kept):
# def photo_template(lang: str, _: str = None) -> str:
#     return f"""You are an image analyzer. Describe the main elements of this image in {lang}."""

OTHER_PROMPTS: Dict[str, Callable[[str, str], str]] = {
    # "photo": photo_template, # Example: if a photo prompt was defined
}
