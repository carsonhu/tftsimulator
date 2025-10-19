import inspect
from importlib import import_module


def _to_display_names(class_names, module_name, is_buff=False):
    """
    Convert a list of class names (strings) from `module_name`
    to their display names. Optionally handle buff-specific overrides.
    """
    mod = import_module(module_name)
    out = []

    for cls_name in class_names:
        obj = getattr(mod, cls_name, None)

        # --- get display name safely ---
        disp = None
        if inspect.isclass(obj):
            disp = getattr(obj, "display_name", None)
            if not isinstance(disp, str):
                try:
                    inst = obj()
                    disp = getattr(inst, "name", cls_name)
                except Exception:
                    disp = cls_name
        else:
            disp = cls_name

        # --- Buff-specific rule: if display name == "NoItem" -> "NoBuff" ---
        if is_buff and disp == "NoItem":
            disp = "NoBuff"

        out.append(disp)

    return out


def buff_display_names(buff_class_names):
    """Return display names for buffs (with 'NoItem' display name → 'NoBuff')."""
    return _to_display_names(buff_class_names, "set15buffs", is_buff=True)


def item_display_names(item_class_names):
    """Return display names for items."""
    return _to_display_names(item_class_names, "set15items", is_buff=False)


def buff_display_map(buff_class_names):
    """Return mapping {DisplayName: ClassName} for buffs."""
    names = buff_display_names(buff_class_names)
    return dict(zip(names, buff_class_names))


def item_display_map(item_class_names):
    """Return mapping {DisplayName: ClassName} for items."""
    names = item_display_names(item_class_names)
    return dict(zip(names, item_class_names))
