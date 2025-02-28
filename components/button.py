from fasthtml.common import Button
def basic_button(text="Button Placeholder"):
    return Button(
        text,
        type="button",
        cls = """
        inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide text-white transition-colors duration-200 rounded-md bg-neutral-950
        hover:bg-neutral-900 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-900 focus:shadow-outline focus:outline-none
        """,
        )
