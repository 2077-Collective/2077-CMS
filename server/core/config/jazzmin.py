JAZZMIN_SETTINGS = {
    "site_title": "2077 Collective CMS",
    
    "site_header": "CMS Dashboard | 2077 Collective",
    
    "site_brand": "CMS Dashboard",
    
    "site_logo": None,
    
    "site_icon": None,
    
    "login_logo": None,
    
    "welcome_sign": "Welcome to the 2077 Authors Dashboard",
    
    "copyright": "2077 Collective",
    
    "topmenu_links": [
        {"name": "HOME",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "ARTICLES", "url": "/admin/research/article/"},        
        {"name": "ABOUT US", "url": "https://2077.xyz/about", "new_window": True},
        {"name": "OUR VALUES", "url": "https://2077.xyz/values", "new_window": True},
        {"name": "SUPPORT US", "url": "https://2077.xyz/support", "new_window": True},
    ],
    "use_google_fonts_cdn": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
    "show_ui_builder": False,
    
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-teal",
    "accent": "accent-teal",
    "navbar": "navbar-teal navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-lime",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "spacelab",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": True
}