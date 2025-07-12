import reflex as rx

config = rx.Config(
    app_name="aiden_companion",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)