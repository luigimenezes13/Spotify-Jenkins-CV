from reactpy import component, html
from typing import Optional, Callable


@component
def Button(
    children,
    variant: str = "primary",
    on_click: Optional[Callable] = None,
    disabled: bool = False,
    class_name: str = "",
    type: str = "button",
):
    base_classes = "btn"
    variant_classes = {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "outline": "btn-outline",
    }
    
    variant_class = variant_classes.get(variant, variant_classes["primary"])
    disabled_class = "btn-disabled" if disabled else ""
    
    classes = f"{base_classes} {variant_class} {disabled_class} {class_name}".strip()
    
    return html.button(
        {
            "class_name": classes,
            "on_click": on_click if not disabled else None,
            "disabled": disabled,
            "type": type,
        },
        children,
    )

