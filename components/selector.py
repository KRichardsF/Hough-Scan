from fasthtml.common import Tr, Td, Input, Div, Table, Thead, Th, Tbody, Tfoot, Button, Svg, ft_hx

def populate_selections(current_settings):
    selection_rows = []
    for i in current_settings.scan_parameters:
        print(current_settings.active_parameters == i)
        selection_rows.append(
            Tr(
                Td(
                    Input(
                        type="text",
                        name="new_name",
                        value=i.scan_name,
                        cls="bg-transparent",
                        onclick="event.stopPropagation();",
                        hx_post="update_name",
                        hx_trigger="change"
                    ),
                cls="px-5 py-4 text-sm font-medium whitespace-nowrap"
                ),
                Td(
                    Input(
                        type="color",
                        name="color",
                        placeholder="some",
                        onclick="event.stopPropagation();",
                        hx_post="update_color",
                        hx_trigger="change",
                        value=i.scan_color
                        ),
                        cls="px-5 py-4 text-sm whitespace-nowrap"

                ),
              cls = f"text-neutral-800 {'bg-neutral-50' if current_settings.active_parameters is i else ''} flex overscroll-y-auto overflow-y-auto",
              hx_post="/select_scan",
              hx_trigger="click",
              hx_target="#sidebar",
              hx_vals={"name":i.scan_name},
            ),
        )
    return selection_rows
def run_selector(current_settings, *args, **kwargs):
    print(current_settings.scan_parameters)
    return (
    Div(
        Div(
            Div(
                Div(
                    Div(
                        Div(
                            Table(
                                Thead(
                                    Tr(
                                        Th("Scan", cls="px-5 py-3 text-xs font-medium text-left uppercase flex grow justify-center"),
                                        Th("Color", cls="px-5 py-3 text-xs font-medium text-left uppercase flex grow justify-center"),
                                        cls="text-neutral-500 flex grow"
                                    ),
                                    cls = "bg-neutral-50 block flex flex-row"
                                ),
                                Tbody(
                                    *populate_selections(current_settings=current_settings),
                                    cls = "overscroll-y-auto overflow-y-auto h-screen",
                                ),
                                Tfoot(
                                    Tr(
                                        Td(
                                            Button(
                                                Svg(
                                                    ft_hx(
                                                        'path',
                                                        stroke_linecap="round",
                                                        stroke_linejoin="round",
                                                        d="M6 12 h 15"
                                                    ),
                                                    xmlns="http://www.w3.org/2000/svg",
                                                    viewBox="0 0 24 24",
                                                    aria_hidden="true",
                                                    stroke="currentColor",
                                                    fill="none",
                                                    stroke_width="2",
                                                    cls="size-4 flex"
                                                    ),
                                                    cls="""px-5 py-3 flex w-full h-full justify-center border-r border-neutral-300
                                                    hover:opacity-75 focus-visible:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black
                                                    active:opacity-100 active:outline-offset-0"
                                                    """,
                                                    hx_post="/remove_scan",
                                                    hx_trigger="click",
                                                    hx_target="#sidebar",
                                                    hx_swap="innerHTML"
                                                ),
                                            Button(
                                                Svg(
                                                    ft_hx(
                                                        'path',
                                                        stroke_linecap="round",
                                                        stroke_linejoin="round",
                                                        d="M12 4.5v15m7.5-7.5h-15"
                                                    ),
                                                    xmlns="http://www.w3.org/2000/svg",
                                                    viewBox="0 0 24 24",
                                                    aria_hidden="true",
                                                    stroke="currentColor",
                                                    fill="none",
                                                    stroke_width="2",
                                                    cls="size-4 flex"
                                                    ),
                                                    cls="""px-5 py-3 flex w-full h-full justify-center
                                                    hover:opacity-75 focus-visible:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black
                                                    active:opacity-100 active:outline-offset-0"
                                                    """,
                                                    hx_post="/add_scan",
                                                    hx_trigger="click",
                                                    hx_target="#sidebar",
                                                    hx_swap="innerHTML"
                                                ),

                                        cls="text-xs font-medium flex w-full justify-around",
                                        colspan="2"
                                        ),
                                        cls="""
                                        flex w-full text-neutral-500
                                        """
                                    ),
                                    cls = "bg-neutral-50 flex",
                                ),
                                cls  = "flex w-full flex-col min-w-full divide-y divide-neutral-200 overscroll-y-auto overflow-y-auto"
                            ),
                            cls = "flex flec-col overflow-hidden border rounded-lg overscroll-y-auto overflow-y-auto"
                        ),
                        cls = "flex flex-col inline-block min-w-full overscroll-y-auto overflow-y-auto px-5 py-3"
                    ),
                    cls = "flex flex-col overflow-x-auto overscroll-y-auto overflow-y-auto"
                ),
                cls= "flex flex-col overscroll-y-auto overflow-y-auto"
            ),
            cls = "flex overscroll-y-auto overflow-y-auto"
        ),
        cls="flex flex-col w-full overscroll-y-auto overflow-y-auto h-1/3 items-center",
        id="scan-select"
    ),
)
