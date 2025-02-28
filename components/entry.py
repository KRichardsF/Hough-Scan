from fasthtml.common import Div, Button, Svg, ft_hx, Input, Label, Script

def ft_path(*c, target_id=None, **kwargs):
    return ft_hx('path', *c, target_id=target_id, **kwargs)

def spinbox(label:str, current_value=1, minimum_value=0, maximum_value=10, decimal_points=0, increment_ammount=1, speed=100, acceleration=20, delay_before_start=200, *args, **kwargs):
    return(
        Div(
            Script(src="scripts/fluid_spinbox.js"),
            Label(
                label,
                fr="counterInput",
                cls="pl-1 text-sm text-neutral-600"
            ),
            Div(
                Button(
                    Svg(
                        ft_hx(
                            'path',
                            stroke_linecap="round",
                            stroke_linejoin="round",
                            d="M19.5 12h-15"
                        ),
                        xmlns="http://www.w3.org/2000/svg",
                        viewBox="0 0 24 24",
                        stroke="currentColor",
                        fill="none",
                        stroke_width="2",
                        cls="size-4",
                    ),
                    **{"@click":"decrement"},
                    **{"@mousedown":"startDecrementing"},
                    **{"@mouseup":"stopCounting"},
                    **{"@mouseleave":"stopCounting"},
                    aria_label="subtract",
                    cls = """
                    flex h-10 items-center justify-center rounded-l-md border border-neutral-300 bg-neutral-50 px-4 py-2 text-neutral-600
                    hover:opacity-75 focus-visible:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
                    focus-visible:outline-black active:opacity-100 active:outline-offset-0
                    """
                ),
                Input(
                    *args,
                    **kwargs,
                    **{"x_model":"currentVal"},
                    **{"@blur":"currentVal = Math.min(maxVal, Math.max(minVal, parseFloat(currentVal).toFixed(decimalPoints)))"},
                    id = "counterInput",
                    type = "text",
                    cls = """
                    border-x-none h-10 w-20 rounded-none border-y border-neutral-300 bg-neutral-50/50 text-center text-neutral-900
                    focus-visible:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-black
                    """
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
                        cls="size-4"
                    ),
                    **{"@click":"increment"},
                    **{"@mousedown":"startIncrementing"},
                    **{"@mouseup":"stopCounting"},
                    **{"@mouseleave":"stopCounting"},
                    cls = """
                    flex h-10 items-center justify-center rounded-r-md border border-neutral-300 bg-neutral-50 px-4 py-2 text-neutral-600
                    hover:opacity-75 focus-visible:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black active:opacity-100 active:outline-offset-0
                    """
                ),
                **{"@dblclick.prevent":""},
                cls="flex items-center"
            ),
        *args,
        x_data=f"counter({{currentVal: {current_value}, minVal: {minimum_value}, maxVal: {maximum_value}, decimalPoints: {decimal_points}, incrementAmount: {increment_ammount}, interval:null, speed:{speed}, acceleration:{acceleration}, delayBeforeStart: {delay_before_start} }})",
        cls="flex flex-col gap-1 m-2",
        **kwargs,
        )
    )

def number_input(label:str,current_value=1, minimum_value=0, maximum_value=10, decimal_points=0, *args, **kwargs):
    return(
        Div(
            Label(
                label,
                fr="numberInput",
                cls="pl-1 text-sm text-neutral-600"
            ),
            Input(
                *args,
                **kwargs,
                **{"x_model":"currentVal"},
                **{"@blur":"currentVal = Math.min(maxVal, Math.max(minVal, parseFloat(currentVal).toFixed(decimalPoints)))"},
                type = "text",
                cls = """
                w-full rounded-md border border-neutral-300 bg-neutral-50 px-2 py-2 text-sm
                focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black disabled:cursor-not-allowed disabled:opacity-75
                """
            ),
        x_data=f"counter({{currentVal: {current_value}, minVal: {minimum_value}, maxVal: {maximum_value}, decimalPoints: {decimal_points}}})",
        cls = "flex w-full max-w-xs flex-col gap-1",
        ),
    )
