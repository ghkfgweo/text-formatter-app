import streamlit as st
import streamlit.components.v1 as components
from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    JsCode
)

from domain.models import (
    GeneratedLink,
    ParsingError,
    Separator
)
from domain.services import (
    APP_TITLE,
    DEFAULT_TEMPLATE,
    build_results_dataframe,
    format_results,
    process_contacts,
)

SEPARATOR_LABELS: dict[str, Separator] = {
    "Linha em branco entre contatos": Separator.DOUBLE_NEWLINE,
    "Um contato por linha": Separator.SINGLE_NEWLINE,
}


def render_copy_button(text: str) -> None:
    """Render a browser clipboard button for `text`."""
    escaped_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    st.iframe(
        f"""
        <button
            onclick="copyResult()"
            style="
                width: 100%;
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #ccc;
                background: white;
                cursor: pointer;
                font-size: 14px;
            "
        >
            Copiar resultado
        </button>

        <script>
            function copyResult() {{
                const text = `{escaped_text}`;

                navigator.clipboard.writeText(text).then(() => {{
                    const button = document.querySelector("button");

                    button.innerText = "✓ Copiado!";

                    setTimeout(() => {{
                        button.innerText = "Copiar resultado";
                    }}, 2000);
                }});
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
        help="Use {name} para inserir o primeiro nome.",
    )


def render_contacts_input() -> str:
    """Render the contacts input."""
    return st.text_area(
        "Lista de contatos",
        height=300,
        help=(
            "Uma pessoa por linha. "
            "O telefone deve ser o último item, sem espaços ou "
            "caracteres especiais."
        ),
    )


def render_separator_input() -> Separator:
    """Render the separator selector for the final results list."""
    label = st.radio(
        "Separador da lista final",
        options=list(SEPARATOR_LABELS),
        horizontal=True,
    )
    return SEPARATOR_LABELS[label]


def render_errors(errors: list[ParsingError]) -> None:
    """Render invalid input lines, along with the reason each one failed."""
    if not errors:
        return

    st.warning(
        f"{len(errors)} linha(s) não puderam ser processadas."
    )

    with st.expander("Ver linhas inválidas"):
        for error in errors:
            st.code(f"{error.line}\n→ {error.reason}")


_LINK_CELL_RENDERER = JsCode(
    """
    class WhatsAppLinkRenderer {
        init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = 'Abrir WhatsApp';
            this.eGui.setAttribute('href', params.value);
            this.eGui.setAttribute('target', '_blank');
            this.eGui.setAttribute('rel', 'noopener noreferrer');
        }

        getGui() {
            return this.eGui;
        }
    }
    """
)


def _build_grid_options(dataframe) -> dict:
    """Build AgGrid options that render the URL column as a clickable link."""
    builder = GridOptionsBuilder.from_dataframe(dataframe)
    builder.configure_column(
        "URL",
        headerName="Link",
        cellRenderer=_LINK_CELL_RENDERER,
    )
    return builder.build()


def render_results_table(links: list[GeneratedLink]) -> None:
    """Render processing results, with a clickable WhatsApp link column."""
    dataframe = build_results_dataframe(links)

    AgGrid(
        dataframe,
        gridOptions=_build_grid_options(dataframe),
        allow_unsafe_jscode=True,
    )


def render_copyable_result(text: str) -> None:
    """Render the final text block, ready to copy and send."""
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
        page_title=APP_TITLE,
        page_icon="📱",
        layout="centered",
    )

    st.title(APP_TITLE)

    template = render_template_input()
    contacts = render_contacts_input()
    separator = render_separator_input()

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
        links, errors = process_contacts(contacts, template)
    except (KeyError, ValueError) as error:
        st.error(f"Template inválido: {error}")
        return

    if not links:
        st.error("Nenhum contato válido encontrado.")
        render_errors(errors)
        return

    st.success(
        f"{len(links)} link(s) gerado(s) com sucesso."
    )

    st.subheader("Resultados")
    render_results_table(links)

    result_text = format_results(links, separator)
    render_copyable_result(result_text)

    render_errors(errors)


if __name__ == "__main__":
    main()