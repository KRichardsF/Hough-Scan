from fasthtml.common import Div, Button, Span

def top_menu(*args, **kwargs):
    return (
        Div(
            Div(
                Div(
                    Div(
                        *args,
                        **kwargs,
                        cls="flex justify-left w-full h-full select-none text-neutral-900"
                    ),
                    cls="w-full h-full p-1 bg-white border rounded-md border-neutral-200/80"
                    ),
                cls="relative top-0 left-0 z-40 w-auto h-10 transition duration-200 ease-out"
                ),
            x_data="{menuBarOpen: false, menuBarMenu: ''}",
            **{'@click.away':'menuBarOpen=false'},
            cls="relative top-0 left-0 z-50 w-auto transition-all duration-150 ease-out"
        ),
    )

def menu_item(name='Button Name Placeholder', *args, **kwargs):
    return(
        Div(
            Button(
                name,
                **{'@click':f"menuBarOpen=true; menuBarMenu='{name}'"},
                **{'@mouseover':f"menuBarMenu='{name}'"},
                **{':class':"{ 'bg-neutral-100' : menuBarOpen && menuBarMenu == 'file'}"},
                cls="""
                rounded text-sm cursor-default flex items-center leading-tight justify-center px-3 py-1.5 h-full
                hover:bg-neutral-100
                """),
            Div(
                *args,
                **kwargs,
                **{'x-show':f"menuBarOpen && menuBarMenu=='{name}'"},
                **{'x-transition:enter':'transition ease-linear duration-100'},
                **{'x-transition:enter-start':'-translate-y-1 opacity-90'},
                **{'x-transition:enter-end':'translate-y-0 opacity-100'},
                **{'x-cloak' : ''},
                cls="""
                absolute top-0 z-50 min-w-[8rem] text-neutral-800 rounded-md border border-neutral-200/70
                bg-white mt-10 text-sm p-1 shadow-md w-48 -translate-x-0.5
                """
            ),
            cls="relative h-full cursor-default",
        )
    )

def menu_selection(name = 'Placeholder', keys = [], *args, **kwargs):
    keycodes = [f"key=='{i}'" if i not in ['Ctrl', 'Shift', 'Alt'] else f"{i.lower()}Key" for i in list(keys)]
    return (
        Button(
        Span(name),
        Span('+'.join([key for key in keys]), cls="ml-auto text-xs tracking-widest text-neutral-400 group-hover:text-neutral-600"),
        *args,
        **kwargs,
        cls= """
        relative flex justify-between w-full cursor-default select-none group items-center rounded px-2 py-1.5
        hover:bg-neutral-100 hover:text-neutral-900 outline-none data-[disabled]:opacity-50 data-[disabled]:pointer-events-none"
        """,
        data_disabled=False,
        hx_trigger=f"click, keyup[{'&&'.join([key for key in keycodes])}] from:body",
        )
    )

def submenu(name = 'Placeholder', *args, **kwargs):
    return(
        Div(cls="h-px my-1 -mx-1 bg-neutral-200"),
        Button(
            Div(
                Span(name),
                cls="flex cursor-default select-none items-center rounded px-2 hover:bg-neutral-100 py-1.5 outline-none"
            ),
            Div(
                Div(
                    *args,
                    **kwargs,
                    cls="z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white p-1 shadow-md animate-in slide-in-from-left-1 w-32"
                ),
                data_submenu="",
                cls="absolute top-0 right-0 invisible mr-1 duration-200 ease-out translate-x-full opacity-0 group-hover:mr-0 group-hover:visible group-hover:opacity-100",
            ),
            cls="relative w-full group"
        ),
        Div(
            cls="h-px my-1 -mx-1 bg-neutral-200"
        )
    )

def submenu_selection(name='Placeholder', *args, **kwargs):
    return (
        Div(
            name,
            *args,
            **kwargs,
            **{"@click":"menuBarOpen=false"},
            cls = "relative flex cursor-default select-none items-center rounded px-2 py-1.5 hover:bg-neutral-100 text-sm outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        )
    )
