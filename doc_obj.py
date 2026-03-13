import json
import os

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QFileDialog, QGraphicsItem

import theme
from context_menu import ContextMenu
from line import Line

# ── Node geometry constants ──────────────────────────────────────
CARD_SIZE = 80  # icon card width & height
ICON_MARGIN = 16  # padding around icon inside card
LABEL_GAP = 8  # gap between card bottom and label
LABEL_H = 32  # label area height (two rows max)
LABEL_W = 120  # label area width (centred on card)
TOTAL_H = CARD_SIZE + LABEL_GAP + LABEL_H  # 120


class DocObj(QGraphicsItem):
    def __init__(self, id, payload, docs_obj_dict, source_file):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.id = id
        self.payload = payload
        self.source_file = source_file

        self.docs_obj_dict = docs_obj_dict
        docs_obj_dict[id] = self

        self.icon = payload.get("icon", "default_icon.png")
        viz = payload.get("viz", {"x": 0, "y": 0})
        self.x = 0
        self.y = 0
        self.rel_x = viz["x"]
        self.rel_y = viz["y"]
        self.w = 100
        self.h = 100
        self.group = False
        self.expandable = False

        self.outbound_lines = []
        self.inbound_lines = []
        self.parent_doc = None
        self.children_docs = []

        self.adding_line_to = False
        self.adding_line_from = False

    # ── Geometry ─────────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        if self.group:
            return QRectF(0, 0, self.w, self.h)
        # Include label area below card; centre label needs some left/right room
        lx = (CARD_SIZE - LABEL_W) / 2  # negative: label is wider than card
        return QRectF(lx, 0, LABEL_W, TOTAL_H)

    # ── Painting ─────────────────────────────────────────────────

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.group:
            self._paint_group(painter)
            return
        self._paint_node(painter)

    def _paint_group(self, painter: QPainter):
        rect = self.boundingRect()
        inner = rect.adjusted(1, 1, -1, -1)
        radius = 14.0
        selected = self.isSelected()

        # Fill
        painter.setPen(Qt.PenStyle.NoPen)
        fill = QColor(theme.GROUP_FILL)
        fill.setAlpha(200)
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(inner, radius, radius)

        # Border
        if selected:
            border_c = QColor(theme.NODE_SELECTED)
            border_c.setAlpha(200)
            pen = QPen(border_c, 1.5, Qt.PenStyle.DashLine)
        else:
            border_c = QColor(theme.NODE_BORDER_GROUP)
            pen = QPen(border_c, 1.0, Qt.PenStyle.DashLine)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawRoundedRect(inner, radius, radius)

        # Corner icon (top-right)
        ico_sz = 28
        ico_x = rect.right() - ico_sz - 10
        ico_y = rect.top() + 10
        pixmap = QPixmap(self.icon)
        if not pixmap.isNull():
            painter.drawPixmap(
                int(ico_x),
                int(ico_y),
                ico_sz,
                ico_sz,
                pixmap.scaled(
                    ico_sz,
                    ico_sz,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )

        # Group label (top-left)
        painter.setPen(QPen(QColor(theme.TEXT_PRIMARY)))
        font = QFont()
        font.setPixelSize(12)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        lbl_rect = QRectF(rect.left() + 12, rect.top() + 12, rect.width() - ico_sz - 24, 22)
        painter.drawText(
            lbl_rect,
            Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(self.id),
        )

    def _paint_node(self, painter: QPainter):
        selected = self.isSelected()
        card = QRectF(0, 0, CARD_SIZE, CARD_SIZE)
        lx = (CARD_SIZE - LABEL_W) / 2

        # ── Shadow ──
        shadow_c = QColor(theme.NODE_SHADOW)
        shadow_c.setAlpha(140)
        shadow_rect = card.adjusted(4, 4, 4, 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_c))
        painter.drawRoundedRect(shadow_rect, 10, 10)

        # ── Card background ──
        painter.setBrush(QBrush(QColor(theme.NODE_BG)))
        if selected:
            pen = QPen(QColor(theme.NODE_SELECTED), 2.0)
        else:
            pen = QPen(QColor(theme.NODE_BORDER), 1.0)
        painter.setPen(pen)
        painter.drawRoundedRect(card.adjusted(0.5, 0.5, -0.5, -0.5), 10, 10)

        # ── Accent strip (top edge when selected) ──
        if selected:
            strip = QRectF(card.left() + 10, card.top() + 0.5, card.width() - 20, 3)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(theme.ACCENT)))
            painter.drawRoundedRect(strip, 1.5, 1.5)

        # ── Icon ──
        icon_sz = CARD_SIZE - 2 * ICON_MARGIN
        pixmap = QPixmap(self.icon)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                int(icon_sz),
                int(icon_sz),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            target = QRectF(
                ICON_MARGIN + (icon_sz - scaled.width()) / 2,
                ICON_MARGIN + (icon_sz - scaled.height()) / 2,
                scaled.width(),
                scaled.height(),
            )
            painter.drawPixmap(target.toRect(), scaled)

        # ── Label ──
        text_color = QColor(theme.TEXT_PRIMARY if selected else theme.TEXT_SECONDARY)
        painter.setPen(QPen(text_color))
        font = QFont()
        font.setPixelSize(11)
        if selected:
            font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)

        label_rect = QRectF(lx, CARD_SIZE + LABEL_GAP, LABEL_W, LABEL_H * (2 if selected else 1))
        painter.drawText(
            label_rect,
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            str(self.id),
        )

    # ── Internal helpers ─────────────────────────────────────────

    def __update_viz(self):
        self.icon = self.payload.get("icon", "default_icon.png")

    def select_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        window.active_obj = self
        window.sidebar.text_area.setText(json.dumps(self.payload, indent=2))
        window.sidebar.id_line.setText(self.id)
        window.sidebar.source_file_line.setText(self.source_file)

    def deselect_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        window.active_obj = None
        text = window.sidebar.text_area.toPlainText()
        if text:
            window.sidebar.text_area.clear()
            try:
                self.payload = json.loads(text)
            except json.JSONDecodeError:
                print("Invalid JSON — changes not saved.")
            window.sidebar.id_line.clear()
            window.sidebar.source_file_line.clear()
            self.__update_viz()

    # ── QGraphicsItem overrides ──────────────────────────────────

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            grid = 20
            new_pos = value
            new_pos.setX(round(new_pos.x() / grid) * grid)
            new_pos.setY(round(new_pos.y() / grid) * grid)
            for line in self.outbound_lines + self.inbound_lines:
                line.update_position()
            if self.parent_doc:
                self.parent_doc.propagate_postion_up()
            return new_pos

        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            scene = self.scene()
            view = scene.views()[0]
            window = view.window() if view else None
            if value:
                if window.active_obj and (
                    window.active_obj.adding_line_to or window.active_obj.adding_line_from
                ):
                    if window.active_obj.adding_line_to:
                        self.add_line_to_select(window.active_obj)
                    elif window.active_obj.adding_line_from:
                        self.add_line_from_select(window.active_obj)
                self.select_square()
                return value
            else:
                self.deselect_square()

        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        self.select_square()
        ContextMenu(self, event)

    # ── Position helpers ─────────────────────────────────────────

    def update_parent_position(self):
        margin = 20
        text_size = 20
        min_x = min(c.pos().x() for c in self.children_docs)
        min_y = min(c.pos().y() for c in self.children_docs)
        max_x = max(c.pos().x() + c.boundingRect().width() for c in self.children_docs)
        max_y = max(c.pos().y() + c.boundingRect().height() for c in self.children_docs) + text_size

        self.setPos(min_x - margin, min_y - margin)
        self.w = max_x - min_x + 2 * margin
        self.h = max_y - min_y + 2 * margin
        self.update()

    def propagate_postion_up(self, include_self=True):
        if include_self:
            self.update_parent_position()
        if self.parent_doc:
            self.parent_doc.propagate_postion_up()

    def propagate_postion_down(self, z_value=0, parent_pos=None):
        self.prepareGeometryChange()
        self.setZValue(z_value)
        pos = self.position_rel_to_abs(parent_pos)
        self.setPos(pos["x"], pos["y"])
        self.update()
        for line in self.outbound_lines + self.inbound_lines:
            line.update_position()
        for child in self.children_docs:
            child.propagate_postion_down(z_value + 1, parent_pos=pos)

    def position_rel_to_abs(self, parent_pos=None):
        if self.parent_doc:
            return {"x": self.rel_x + parent_pos["x"], "y": self.rel_y + parent_pos["y"]}
        return {"x": self.rel_x, "y": self.rel_y}

    def position_abs_to_rel(self):
        if self.parent_doc:
            return {
                "x": self.pos().x() - self.parent_doc.pos().x(),
                "y": self.pos().y() - self.parent_doc.pos().y(),
            }
        return {"x": self.pos().x(), "y": self.pos().y()}

    # ── Node / Group mode ────────────────────────────────────────

    def make_group(self):
        self.group = True
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def make_final(self):
        self.group = False
        self.setZValue(99)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    # ── Source / Sink queries ────────────────────────────────────

    def get_sources(self):
        return [line.source_doc for line in self.inbound_lines]

    def get_sinks(self):
        return [line.sink_doc for line in self.outbound_lines]

    # ── Child management ─────────────────────────────────────────

    def add_child_document(self, node):
        self.children_docs.append(node)

    def remove_child_document(self, node):
        self.children_docs.remove(node)

    # ── Line operations ──────────────────────────────────────────

    def create_new_source(self):
        new_obj = DocObj(
            "new",
            {"icon": "default_icon.png", "viz": {"x": self.pos().x(), "y": self.pos().y() - 140}},
            self.docs_obj_dict,
            self.source_file,
        )
        new_obj.make_final()
        new_obj.setPos(self.pos().x(), self.pos().y() - 140)
        line = Line(new_obj, self)
        new_obj.outbound_lines.append(line)
        self.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
        if "sources" in self.payload:
            self.payload["sources"].append(new_obj.id)
        else:
            self.payload["sources"] = [new_obj.id]
        return new_obj

    def create_new_sink(self):
        new_obj = DocObj(
            "new",
            {
                "icon": "default_icon.png",
                "sources": [self.id],
                "viz": {"x": self.pos().x(), "y": self.pos().y() + 140},
            },
            self.docs_obj_dict,
            self.source_file,
        )
        new_obj.make_final()
        new_obj.setPos(self.pos().x(), self.pos().y() + 140)
        line = Line(self, new_obj)
        self.outbound_lines.append(line)
        new_obj.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
        return new_obj

    def add_line_to(self):
        self.adding_line_to = True

    def add_line_from(self):
        self.adding_line_from = True

    def add_line_to_select(self, obj_to):
        if obj_to == self or obj_to in self.get_sources():
            return
        line = Line(self, obj_to)
        self.outbound_lines.append(line)
        obj_to.inbound_lines.append(line)
        self.scene().addItem(line)
        self.adding_line_to = False

    def add_line_from_select(self, obj_from):
        if obj_from == self or obj_from in self.get_sinks():
            return
        line = Line(obj_from, self)
        self.inbound_lines.append(line)
        obj_from.outbound_lines.append(line)
        self.scene().addItem(line)
        obj_from.adding_line_from = False

    # ── Collapse / Expand ────────────────────────────────────────

    def collapse(self):
        for child in self.children_docs:
            child.collapse()
            child.setVisible(False)
            for line in child.outbound_lines + child.inbound_lines:
                line.setVisible(False)
        self.make_final()
        self.expandable = True
        self.propagate_postion_up(False)

    def expand(self):
        if not self.expandable:
            return
        base_z = 0
        if self.parent_doc:
            base_z = self.parent_doc.zValue() + 1
        self.setZValue(base_z)
        self.propagate_postion_down(base_z, {"x": self.pos().x(), "y": self.pos().y()})
        for child in self.children_docs:
            child.setVisible(True)
            for line in child.outbound_lines + child.inbound_lines:
                line.setVisible(True)
        self.make_group()
        self.propagate_postion_up()
        self.expandable = False

    def set_group(self, group):
        group_obj = self.docs_obj_dict[group]
        group_obj.add_child_document(self)
        self.parent_doc = group_obj

    # ── Icon / link helpers ──────────────────────────────────────

    def change_icon(self, icon_path):
        self.payload["icon"] = icon_path
        self.__select_square()
        self.__update_viz()
        self.update()

    def context_change_icon(self):
        icon_file, _ = QFileDialog.getOpenFileName(
            None, "Select Icon", "", "Icon Files (*.ico *.jpg *.jpeg *.png)"
        )
        if icon_file:
            relative_path = os.path.relpath(icon_file, os.getcwd())
            self.change_icon(relative_path)

    def open_in_browser(self):
        link = self.payload.get("link")
        if link:
            import webbrowser

            webbrowser.open(link)
        else:
            print("No link specified for this object.")

    # ── Delete ───────────────────────────────────────────────────

    def delete(self):
        scene = self.scene()
        if scene and scene.views():
            self.deselect_square()

        for child in list(self.children_docs):
            child.delete()

        if self.parent_doc:
            self.parent_doc.children_docs.remove(self)

        scene = self.scene()
        if scene is None:
            return

        for line in list(self.outbound_lines):
            line.sink_doc.inbound_lines.remove(line)
            scene.removeItem(line)

        for line in list(self.inbound_lines):
            line.source_doc.outbound_lines.remove(line)
            scene.removeItem(line)

        del self.docs_obj_dict[self.id]
        scene.removeItem(self)
