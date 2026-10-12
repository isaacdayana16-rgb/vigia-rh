"""Pruebas de src/reportes.py: el PDF debe generarse en tmp_path, nunca en output/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import reportes


class TestGenerarReporte:
    def test_pdf_se_genera_en_tmp(self, tmp_path, monkeypatch):
        """El PDF se escribe en la ruta parcheada y empieza con %PDF."""
        salida_dir = tmp_path / "output"
        salida_pdf = salida_dir / "reporte_test.pdf"
        monkeypatch.setattr(reportes, "OUTPUT_DIR", str(salida_dir))
        monkeypatch.setattr(reportes, "PDF_PATH", str(salida_pdf))
        # Sin imagen SHAP: fuerza la rama alternativa, aislado de output/
        monkeypatch.setattr(reportes, "SHAP_PATH", str(tmp_path / "no_existe.png"))

        ruta = reportes._generar_reporte()

        assert Path(ruta) == salida_pdf
        assert salida_pdf.exists()
        contenido = salida_pdf.read_bytes()
        assert contenido.startswith(b"%PDF")
        assert len(contenido) > 0

    def test_pdf_no_toca_output_real(self, tmp_path, monkeypatch):
        """La generación no modifica ningún archivo del output/ real del repo."""
        output_real = ROOT / "output"
        antes = {
            p.name: (p.stat().st_size, p.stat().st_mtime_ns)
            for p in output_real.iterdir()
        }
        salida_pdf = tmp_path / "reporte_test.pdf"
        monkeypatch.setattr(reportes, "OUTPUT_DIR", str(tmp_path))
        monkeypatch.setattr(reportes, "PDF_PATH", str(salida_pdf))
        monkeypatch.setattr(reportes, "SHAP_PATH", str(tmp_path / "no_existe.png"))

        reportes._generar_reporte()

        despues = {
            p.name: (p.stat().st_size, p.stat().st_mtime_ns)
            for p in output_real.iterdir()
        }
        assert despues == antes
        assert salida_pdf.exists()
