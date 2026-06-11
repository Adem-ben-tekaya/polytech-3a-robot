STYLE = """
    QMainWindow, QWidget {
        background-color: #0d0f14;
        color: #e8eaf0;
    }

    QLabel#titre {
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 4px;
        color: #ff4f6d;
    }

    QLabel#sous_titre {
        font-size: 13px;
        letter-spacing: 6px;
        color: #dadce6;
    }

    QPushButton {
        border: 1px solid #2a2d3a;
        border-radius: 4px;
        padding: 8px 18px;
        font-size: 13px;
        font-family: 'Consolas', monospace;
        letter-spacing: 1px;
        background-color: #161820;
        color: #dadce6;
    }

    QPushButton:hover   { background-color: #1e2130; border-color: #ff4f6d; color: #ff4f6d; }
    QPushButton:pressed { background-color: #ff4f6d; color: #0d0f14; }

    QPushButton#btn_start {
        background-color: #1a3a2a;
        border-color: #2ecc71;
        color: #2ecc71;
        font-weight: bold;
        letter-spacing: 2px;
    }

    QPushButton#btn_start:hover   { background-color: #2ecc71; color: #0d0f14; }

    QPushButton#btn_stop {
        background-color: #3a1a1a;
        border-color: #ff4f6d;
        color: #ff4f6d;
        font-weight: bold;
        letter-spacing: 2px;
    }

    QPushButton#btn_stop:hover   { background-color: #ff4f6d; color: #0d0f14; }

    QTableWidget {
        background-color: #10121a;
        border: 1px solid #1e2130;
        gridline-color: #1a1d2a;
        alternate-background-color: #13151e;
        color: #e8eaf0;
        font-size: 13px;
    }

    QHeaderView::section {
        background-color: #161820;
        color: #dadce6;
        border: none;
        border-bottom: 1px solid #2a2d3a;
        padding: 6px;
        font-size: 12px;
        letter-spacing: 2px;
    }

    QTextEdit {
        background-color: #0a0c10;
        border: 1px solid #1e2130;
        color: #7a9f7a;
        font-size: 13px;
        font-family: 'Consolas', monospace;
    }

    QLineEdit {
        background-color: #161820;
        border: 1px solid #2a2d3a;
        color: #dadce6;
        padding: 4px;
        font-size: 13px;
        font-family: 'Consolas', monospace;
    }

    QLabel#section {
        color: #dadce6;
        font-size: 12px;
        letter-spacing: 3px;
        padding: 4px 0px 2px 0px;
    }

    QFrame#separator {
        background-color: #1e2130;
        max-height: 1px;
    }

    QStatusBar {
        background-color: #0a0c10;
        color: #dadce6;
        font-size: 12px;
        border-top: 1px solid #1e2130;
    }

    QSplitter::handle { background-color: #1e2130; }
"""

COLOR_MAP = {
    'N': ('#3a3a3a', 'NOIR'),
    'P': ('#9b59b6', 'MAUVE'),
    'B': ('#2980b9', 'BLEU'),
    'Y': ('#f1c40f', 'JAUNE'),
    'C': ('#1abc9c', 'CYAN'),
    'G': ('#27ae60', 'VERT'),
    'R': ("#c92323", 'ROUGE'),
}