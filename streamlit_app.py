import streamlit as st
import streamlit.components.v1 as components

from models import GeneratedLink

from services import (
    format_results,
    process_contacts,
    build_results_dataframe
)

DEFAULT_TEMPLATE = "Bom dia, {name}! Tudo bem?"


def render_copy_button(text: str) -> None:
    """Render a browser clipboard button."""
    escaped_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    st.iframe(
        f"""
        <button
            onclick="copyText()"
            style="
                width: 100%;
                padding: 8px;
                cursor: pointer;
            "
        >
            Copiar resultado
        </button>

        <script>
            function copyText() {{
                const text = `{escaped_text}`;

                navigator.clipboard.writeText(text);
            }}
        </script>
        """,
        height=50,
    )


def render_template_input() -> str:
    """Render the message template input."""
    return st.text_area(
        "Template da mensagem",
        value=DEFAULT_TEMPLATE,
        help="Use {nome} para inserir o primeiro nome.",
    )


def render_contacts_input() -> str:
    """Render the contacts input."""
    return st.text_area(
        "Lista de contatos",
        height=300,
        help=(
            "Uma pessoa por linha. "
            "O telefone deve ser o último item."
        ),
    )
    
    
def render_errors(errors: list[str]) -> None:
    """Render invalid input lines."""
    if not errors:
        return

    st.warning(
        f"{len(errors)} linha(s) não puderam ser processadas."
    )

    with st.expander("Ver linhas inválidas"):
        for error in errors:
            st.code(error)


def render_results_table(
    links: list[GeneratedLink],
) -> None:
    """Render processing results."""
    
    dataframe = build_results_dataframe(links)
    
    st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True,
        column_config={
            "Nome": st.column_config.TextColumn("Nome"),
            "Telefone": st.column_config.TextColumn("Telefone"),
            "Link": st.column_config.LinkColumn(
                "Link",
                display_text="Abrir WhatsApp"
            )
        }
    )


# def render_copy_button(text: str) -> None:
#     escaped_text = (
#         text.replace("\\", "\\\\")
#         .replace("`", "\\`")
#         .replace("${", "\\${")
#     )

#     html = f"""
#     <button
#         onclick="copyResult()"
#         style="
#             width: 100%;
#             padding: 8px 16px;
#             border-radius: 6px;
#             border: 1px solid #ccc;
#             background: white;
#             cursor: pointer;
#             font-size: 14px;
#         "
#     >
#         Copiar resultado
#     </button>

#     <script>
#         function copyResult() {{
#             const text = `{escaped_text}`;

#             navigator.clipboard.writeText(text).then(() => {{
#                 const button = document.querySelector("button");

#                 button.innerText = "✓ Copiado!";

#                 setTimeout(() => {{
#                     button.innerText = "Copiar resultado";
#                 }}, 2000);
#             }});
#         }}
#     </script>
#     """

#     components.html(
#         html,
#         height=45,
#     )

def render_copyable_result(
    text: str,
) -> None:
    st.subheader("Texto para copiar")

    st.text_area(
        "Resultado",
        value=text,
        height=250,
        label_visibility="collapsed",
    )

    render_copy_button(text)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Gerador de Links de Whatsapp",
        page_icon="📱",
        layout="centered",
    )

    st.title("Gerador de Links de Whatsapp")

    template = render_template_input()
    contacts = render_contacts_input()

    generate = st.button(
        "🔗 Gerar links",
        type="primary",
        width="stretch",
    )

    if not generate:
        return

    if not contacts.strip():
        st.error("Informe pelo menos um contato.")
        return

    try:
        links, errors = process_contacts(
            contacts,
            template,
        )
    except (KeyError, ValueError) as error:
        st.error(f"Template inválido: {error}")
        return

    if not links:
        st.error("Nenhum contato válido encontrado.")
        return

    st.success(
        f"{len(links)} link(s) gerado(s) com sucesso."
    )

    st.subheader("Resultados")
    render_results_table(links)

    result_text = format_results(links)
    render_copyable_result(result_text)

    render_errors(errors)


if __name__ == "__main__":
    main()