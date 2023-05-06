import tempfile
import pandas as pd
from io import BytesIO
from fastapi import responses


def get_excel_file(filename: str, df_list: dict):
    stream = BytesIO()
    writer = pd.ExcelWriter(stream)
    for key, df in df_list.items():
        df.to_excel(writer, sheet_name=key, index=False)
        worksheet = writer.sheets[key]
        worksheet.autofit()
    writer.close()
    stream.seek(0)
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".xlsx", delete=False) as temp_file:
        temp_file.write(stream.read())
        return responses.FileResponse(
            temp_file.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}",
                     "Access-Control-Expose-Headers": "Content-Disposition",
                     }
        )
