import flet as ft
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io
import base64
import tkinter as tk
from tkinter import filedialog


def apply_filter(img, filter_type):
    filters = {
        "Blur": ImageFilter.BLUR,
        "Contour": ImageFilter.CONTOUR,
        "Detail": ImageFilter.DETAIL,
        "Edge Enhance": ImageFilter.EDGE_ENHANCE,
        "Edge Enhance More": ImageFilter.EDGE_ENHANCE_MORE,
        "Emboss": ImageFilter.EMBOSS,
        "Find Edges": ImageFilter.FIND_EDGES,
        "Sharpen": ImageFilter.SHARPEN,
        "Smooth": ImageFilter.SMOOTH,
        "Smooth More": ImageFilter.SMOOTH_MORE
    }
    enhancements = {
        "Enhance Brightness": ImageEnhance.Brightness(img).enhance(1.5),
        "Enhance Contrast": ImageEnhance.Contrast(img).enhance(1.5),
        "Enhance Color": ImageEnhance.Color(img).enhance(1.5),
        "Enhance Sharpness": ImageEnhance.Sharpness(img).enhance(2)
    }
    operations = {
        "Grayscale": ImageOps.grayscale,
        "Invert": lambda img: ImageOps.invert(img.convert("RGB")),
        "Mirror": ImageOps.mirror,
        "Flip": ImageOps.flip,
        "Solarize": lambda img: ImageOps.solarize(img, threshold=128),
        "Posterize": lambda img: ImageOps.posterize(img, bits=4),
        "Equalize": ImageOps.equalize,
        "Autocontrast": ImageOps.autocontrast
    }

    if filter_type in filters:
        return img.filter(filters[filter_type])
    elif filter_type in enhancements:
        return enhancements[filter_type]
    elif filter_type in operations:
        return operations[filter_type](img)
    return img


def img_to_base64(img):
    with io.BytesIO() as buffer:
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()


def base64_to_img(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))


def main(page: ft.Page):
    page.title = "Editor de Imagens - Flet"
    page.theme_mode = ft.ThemeMode.DARK

    img_display = ft.Image(src="", width=400, height=300)

    filtros = [
        "Blur", "Contour", "Detail", "Edge Enhance", "Edge Enhance More",
        "Emboss", "Find Edges", "Sharpen", "Smooth", "Smooth More",
        "Grayscale", "Invert", "Mirror", "Flip", "Solarize", "Posterize",
        "Equalize", "Autocontrast", "Enhance Brightness",
        "Enhance Contrast", "Enhance Color", "Enhance Sharpness"
    ]
    filter_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(f) for f in filtros],
        width=200,
        value="Blur"
    )

    original_image = None
    history = []

    def upload_image(e: ft.FilePickerResultEvent):
        nonlocal original_image, history
        if not e.files:
            return
        file = e.files[0]

        if file.path:  # Desktop
            with open(file.path, "rb") as f:
                img_data = f.read()
        elif file.content:  # Web
            img_data = base64.b64decode(file.content)
        else:
            return

        img = Image.open(io.BytesIO(img_data))
        original_image = img_to_base64(img)
        history.clear()
        img_display.src_base64 = original_image
        img_display.update()

    def apply_selected_filter(e):
        nonlocal history
        if not img_display.src_base64:
            return
        history.append(img_display.src_base64)
        img = base64_to_img(img_display.src_base64)
        img = apply_filter(img, filter_dropdown.value)
        img_display.src_base64 = img_to_base64(img)
        img_display.update()

    def undo(e):
        nonlocal history
        if history:
            img_display.src_base64 = history.pop()
            img_display.update()

    def reset_image(e):
        nonlocal original_image, history
        if original_image:
            history.clear()
            img_display.src_base64 = original_image
            img_display.update()

    def download_image(e):
        if not img_display.src_base64:
            return
        if page.platform == "web":
            data_url = "data:image/png;base64," + img_display.src_base64
            js_code = """
            var a = document.createElement("a");
            a.href = arguments[0];
            a.download = "imagem_com_filtros.png";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            """
            page.eval_js(js_code, [data_url])
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png", filetypes=[("PNG Files", "*.png")]
            )
            if file_path:
                img_bytes = base64.b64decode(img_display.src_base64)
                img = Image.open(io.BytesIO(img_bytes))
                img.save(file_path, "PNG")
            root.destroy()

    file_picker = ft.FilePicker(on_result=upload_image)
    page.overlay.append(file_picker)

    btn_upload = ft.ElevatedButton(
        "Carregar Imagem", on_click=lambda _: file_picker.pick_files())
    btn_apply = ft.ElevatedButton(
        "Aplicar Filtro", on_click=apply_selected_filter)
    btn_undo = ft.ElevatedButton("Desfazer", on_click=undo)
    btn_reset = ft.ElevatedButton("Voltar ao Original", on_click=reset_image)
    btn_download = ft.ElevatedButton("Baixar Imagem", on_click=download_image)

    page.add(
        ft.Column(
            [
                btn_upload,
                img_display,
                filter_dropdown,
                ft.Row(
                    [btn_apply, btn_undo, btn_reset, btn_download],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


ft.app(target=main)
