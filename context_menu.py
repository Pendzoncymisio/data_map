from PyQt6.QtWidgets import QInputDialog, QMenu

import theme


class ContextMenu(QMenu):
    """Dark-styled right-click context menu for DocObj nodes."""

    def __init__(self, caller, event):
        super().__init__()

        # Apply dark styling inline (inherits from app stylesheet but be explicit)
        self.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.BG_SECONDARY};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_LIGHT};
                border-radius: 8px;
                padding: 5px 4px;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 7px 28px 7px 14px;
                border-radius: 4px;
                margin: 1px 0;
            }}
            QMenu::item:selected {{
                background-color: {theme.ACCENT_SUBTLE};
                color: {theme.TEXT_PRIMARY};
            }}
            QMenu::item:disabled {{
                color: {theme.TEXT_MUTED};
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme.BORDER};
                margin: 4px 8px;
            }}
        """)

        self.caller = caller

        # ── Add Node sub-menu ──
        add_node_menu = self.addMenu("  Add Node")
        add_source_action = add_node_menu.addAction("  Add Source")
        add_sink_action = add_node_menu.addAction("  Add Sink")

        # ── Add Line sub-menu ──
        add_line_menu = self.addMenu("  Add Line")
        add_line_to_action = add_line_menu.addAction("  Add Line To…")
        add_line_from_action = add_line_menu.addAction("  Add Line From…")

        self.addSeparator()

        # ── Expand / Collapse ──
        expand_action = self.addAction("  Expand")
        collapse_action = self.addAction("  Collapse")

        self.addSeparator()

        # ── Edit ──
        set_group_action = self.addAction("  Set Group…")
        change_icon_action = self.addAction("  Change Icon…")
        open_browser_action = self.addAction("  Open in Browser")

        self.addSeparator()

        # ── Delete sub-menu (prevents accidental deletion) ──
        delete_menu = self.addMenu("  Delete")
        delete_action = delete_menu.addAction("  Confirm Delete")
        delete_action.setObjectName("danger")

        # ── Set enabled states ──
        expand_action.setEnabled(caller.expandable)
        collapse_action.setEnabled(bool(caller.group))

        # ── Execute ──
        action = self.exec(event.screenPos())

        if action == expand_action:
            caller.expand()
        elif action == collapse_action:
            caller.collapse()
        elif action == add_source_action:
            caller.create_new_source()
        elif action == add_sink_action:
            caller.create_new_sink()
        elif action == add_line_to_action:
            caller.add_line_to()
        elif action == add_line_from_action:
            caller.add_line_from()
        elif action == set_group_action:
            group, ok = QInputDialog.getText(self, "Set Group", "Enter group name:")
            if ok and group:
                caller.set_group(group)
        elif action == change_icon_action:
            caller.context_change_icon()
        elif action == open_browser_action:
            caller.open_in_browser()
        elif action == delete_action:
            caller.delete()
