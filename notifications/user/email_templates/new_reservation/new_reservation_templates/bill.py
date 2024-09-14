BILL_TEMPLATE = """<table width="100%" cellpadding="0" cellspacing="0" border="0" style="{style}">
  <tr>
    <td colspan="2">
      <h3 style="margin: 0; padding: 0; width: 100%; font-weight: 500;">Детализация по дням:</h3>
    </td>
  </tr>
  <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  {bill_positions}
</table>
<tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>"""

BILL_POSITION_TEMPLATE = """<tr style="margin: 0; padding: 0;" width="100%">
    <td colspan="2" width="50%" style="vertical-align: middle; height: min-content; white-space: nowrap;">
    <img width="18px" height="18px" src="{bill_position_icon}" style="display: inline-block; vertical-align: middle; padding-right: 10px;"/>
    <p style="display: inline-block; margin: 0; vertical-align: middle; height: min-content; white-space: nowrap;">
        {bill_position_description}
    </p>
    </td>
    <td colspan="2" width="50%">
    <p style="margin: 0; height: min-content; text-align: right;">
        {bill_position_price} ₽
    </p>
    </td>
</tr>
<tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>"""
