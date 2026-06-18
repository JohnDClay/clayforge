"""
ClayForge Foundational UI Elements

These are the first "real" components that will power user applications.
They demonstrate the full lifecycle: beautiful Tailwind defaults + WS update support.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..element import Element


@dataclass
class Text(Element):
    """Simple text / paragraph with excellent defaults."""

    content: str = ""
    tag: str = "p"
    size: str = "base"  # sm, base, lg, xl, 2xl

    def to_html(self) -> str:
        size_map = {
            "sm": "text-sm",
            "base": "text-base",
            "lg": "text-lg",
            "xl": "text-xl",
            "2xl": "text-2xl font-semibold tracking-tight",
        }
        cls = f"{size_map.get(self.size, 'text-base')} text-zinc-200 {self.classes or ''}".strip()
        return f'<{self.tag} id="{self.id}" class="{cls}">{self.content}</{self.tag}>'

    def _html_tag(self) -> str:
        return self.tag


@dataclass
class Button(Element):
    """Primary beautiful button with variants. Full event support."""

    label: str = "Button"
    variant: str = "primary"  # primary | secondary | ghost | danger
    size: str = "md"

    def __post_init__(self) -> None:
        super().__post_init__()
        # Auto wire a data attribute so the tiny client JS can find us easily
        self.attrs.setdefault("data-cf-role", "button")

    def to_html(self) -> str:
        base = (
            "inline-flex items-center justify-center gap-2 font-semibold rounded-2xl "
            "transition-all active:scale-[0.985] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-zinc-950 "
            "disabled:opacity-60 disabled:pointer-events-none select-none"
        )

        variants = {
            "primary": "bg-white text-zinc-950 hover:bg-zinc-100 shadow-sm focus:ring-white/70 px-5",
            "secondary": "bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700 focus:ring-zinc-400 px-5",
            "ghost": "hover:bg-zinc-800 text-zinc-300 hover:text-white px-4",
            "danger": "bg-red-600 hover:bg-red-500 text-white px-5",
        }
        sizes = {"sm": "h-9 text-sm px-4", "md": "h-10 text-sm", "lg": "h-12 text-base px-6"}

        cls = f"{base} {variants.get(self.variant, variants['primary'])} {sizes.get(self.size, sizes['md'])} {self.classes or ''}".strip()

        return (
            f'<button id="{self.id}" type="button" class="{cls}" '
            f'data-event="click" {self._extra_attrs()}>{self.label}</button>'
        )

    def _extra_attrs(self) -> str:
        return " ".join(f'{k}="{v}"' for k, v in self.attrs.items())


@dataclass
class Card(Element):
    """shadcn/ui inspired card with header + content."""

    title: str | None = None
    subtitle: str | None = None

    def to_html(self) -> str:
        header = ""
        if self.title:
            header = (
                '<div class="px-6 pt-6 pb-3">'
                f'<div class="font-semibold text-lg tracking-tight text-white">{self.title}</div>'
            )
            if self.subtitle:
                header += f'<div class="text-xs text-zinc-400 mt-0.5">{self.subtitle}</div>'
            header += "</div>"

        body = "".join(c.to_html() for c in self.children)
        if not body:
            body = '<div class="px-6 pb-6 text-sm text-zinc-400">Empty card</div>'

        cls = f"bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-sm {self.classes or ''}".strip()

        return (
            f'<div id="{self.id}" class="{cls}">{header}<div class="px-6 pb-6">{body}</div></div>'
        )


@dataclass
class Row(Element):
    """Horizontal flex container with great spacing defaults."""

    gap: str = "4"  # Tailwind gap unit
    align: str = "center"

    def to_html(self) -> str:
        cls = f"flex flex-wrap items-{self.align} gap-{self.gap} {self.classes or ''}".strip()
        inner = "".join(c.to_html() for c in self.children)
        return f'<div id="{self.id}" class="{cls}">{inner}</div>'


@dataclass
class Column(Element):
    """Vertical stack (most common layout primitive)."""

    gap: str = "3"

    def to_html(self) -> str:
        cls = f"flex flex-col gap-{self.gap} {self.classes or ''}".strip()
        inner = "".join(c.to_html() for c in self.children)
        return f'<div id="{self.id}" class="{cls}">{inner}</div>'


# ------------------------------------------------------------------
# Additional small, high-utility components (added in rendering milestone)
# These keep the same beautiful zinc/indigo Tailwind language as the rest.
# ------------------------------------------------------------------


@dataclass
class Divider(Element):
    """Elegant horizontal separator. Perfect between sections or cards."""

    def to_html(self) -> str:
        cls = f"h-px bg-zinc-800 my-4 {self.classes or ''}".strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        return f'<div id="{self.id}" class="{cls}"{style}{extra}></div>'


@dataclass
class Badge(Element):
    """Compact, beautiful status / label pill. Multiple semantic variants."""

    text: str = ""
    variant: str = "default"  # default | success | warning | danger | info

    def to_html(self) -> str:
        variants = {
            "default": "bg-zinc-800 text-zinc-300 border border-zinc-700",
            "success": "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
            "warning": "bg-amber-500/10 text-amber-400 border border-amber-500/30",
            "danger": "bg-red-500/10 text-red-400 border border-red-500/30",
            "info": "bg-indigo-500/10 text-indigo-400 border border-indigo-500/30",
        }
        vcls = variants.get(self.variant, variants["default"])
        cls = f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {vcls} {self.classes or ''}".strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        return f'<span id="{self.id}" class="{cls}"{style}{extra}>{self.text}</span>'


@dataclass
class TextInput(Element):
    """Beautiful styled text input stub.

    Renders with perfect dark-mode Tailwind defaults matching the rest of ClayForge.
    Supports future event roundtrips (change/input) via the standard element protocol.
    """

    placeholder: str = "Type here..."
    value: str = ""
    # Optional label support can be added later by composing with Text

    def __post_init__(self) -> None:
        super().__post_init__()
        self.attrs.setdefault("data-cf-role", "input")
        # "change" gives committed value; "input" would be live keystroke (future)
        self.attrs.setdefault("data-event", "change")

    def to_html(self) -> str:
        cls = (
            "w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl "
            "text-sm text-zinc-200 placeholder:text-zinc-500 "
            "focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 "
            "transition-all " + (self.classes or "")
        ).strip()

        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""

        return (
            f'<input id="{self.id}" type="text" '
            f'value="{self.value}" placeholder="{self.placeholder}" '
            f'class="{cls}"{style}{extra}>'
        )


# ------------------------------------------------------------------
# Additional core form controls (added to make "rich built-ins" real)
# ------------------------------------------------------------------


@dataclass
class Select(Element):
    """Beautiful select/dropdown. Supports options, value, change events."""

    label: str = "Choose"
    options: list[str] = field(default_factory=lambda: ["Option A", "Option B"])
    value: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.value and self.options:
            self.value = self.options[0]
        self.attrs.setdefault("data-event", "change")

    def to_html(self) -> str:
        opts_html = "".join(
            f'<option value="{o}" {"selected" if o == self.value else ""}>{o}</option>'
            for o in self.options
        )
        cls = (
            "w-full bg-zinc-950 border border-zinc-800 text-sm rounded-2xl px-4 py-2.5 "
            "text-zinc-200 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 "
            "transition-all " + (self.classes or "")
        ).strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        label_html = (
            f'<div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">{self.label}</div>'
            if self.label
            else ""
        )
        return (
            f'<div id="{self.id}" class="w-full">'
            f"{label_html}"
            f'<select class="{cls}"{style}{extra}>{opts_html}</select>'
            f"</div>"
        )


@dataclass
class Checkbox(Element):
    """Styled checkbox with label. checked state + change events."""

    label: str = "Option"
    checked: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        self.attrs.setdefault("data-event", "change")
        self.attrs.setdefault("data-cf-role", "checkbox")

    def to_html(self) -> str:
        cls = (
            "w-4 h-4 accent-indigo-500 bg-zinc-950 border border-zinc-700 rounded "
            "focus:ring-1 focus:ring-offset-2 focus:ring-offset-zinc-950 focus:ring-indigo-500 "
            + (self.classes or "")
        ).strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        checked = "checked" if self.checked else ""
        return (
            f'<label id="{self.id}" class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">'
            f'<input type="checkbox" class="{cls}" {checked}{style}{extra}>'
            f"<span>{self.label}</span>"
            f"</label>"
        )


@dataclass
class TextArea(Element):
    """Multi-line text input. Nice defaults, supports change events."""

    placeholder: str = "Enter text..."
    value: str = ""
    rows: int = 4

    def __post_init__(self) -> None:
        super().__post_init__()
        self.attrs.setdefault("data-event", "change")
        self.attrs.setdefault("data-cf-role", "textarea")

    def to_html(self) -> str:
        cls = (
            "w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl "
            "text-sm text-zinc-200 placeholder:text-zinc-500 "
            "focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 "
            "transition-all resize-y " + (self.classes or "")
        ).strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        return (
            f'<textarea id="{self.id}" rows="{self.rows}" '
            f'placeholder="{self.placeholder}" class="{cls}"{style}{extra}>{self.value}</textarea>'
        )


@dataclass
class FileUpload(Element):
    """Simple file input with filename preview. Fires change with file name (for server handlers).
    Real binary upload can use @app.api or form post; this gives beautiful zero-boilerplate UX.
    """

    label: str = "Choose file"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.attrs.setdefault("data-event", "change")
        self.attrs.setdefault("data-cf-role", "file")

    def to_html(self) -> str:
        cls = (
            "block w-full text-sm text-zinc-400 file:mr-4 file:py-2 file:px-4 "
            "file:rounded-2xl file:border-0 file:text-sm file:font-semibold "
            "file:bg-white file:text-zinc-950 hover:file:bg-zinc-100 "
            "cursor-pointer " + (self.classes or "")
        ).strip()
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""
        return (
            f'<div id="{self.id}" class="w-full">'
            f'<div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">{self.label}</div>'
            f'<input type="file" class="{cls}"{style}{extra} '
            f"onchange=\"const n=this.files[0]?this.files[0].name:'';const s=document.getElementById('{self.id}-name');if(s)s.textContent=n||'No file';this.dispatchEvent(new CustomEvent('cf-event',{{bubbles:true,detail:{{id:'{self.id}',type:'change',value:n}}}}));\">"
            f'<div id="{self.id}-name" class="text-[10px] mt-1 text-emerald-400 font-mono">No file selected</div>'
            f"</div>"
        )
