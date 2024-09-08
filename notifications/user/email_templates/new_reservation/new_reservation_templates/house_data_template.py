HOUSE_DATA_TEMPLATE = """<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #F3F3F3; padding: 20px; border-radius: 15px; border: 2px dashed black; box-sizing: border-box; max-width: 500px; margin: 0 auto;">
  <tr style="padding-bottom: 100px; margin-bottom: 123px; ">
    <td colspan="2">
      <img width="100%" height="auto" src="{house_image}" style="border-radius: 15px;" />
    </td>
  </tr>
  <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>
  <tr>
    <td style="vertical-align: middle;">
      <img width="21px" height="21px" src="{house_location_icon}" style="display: inline-block; vertical-align: middle;"/>
      <p style="margin: 0; display: inline-block; vertical-align: middle;">Адрес:</p>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <a href="{house_location_link}" style="color: black;">
        <p>{house_location_text}</p>
      </a>
    </td>
  </tr>
</table>
<tr><td colspan="2" style="line-height: 0; height: 10px;">&nbsp;</td></tr>"""