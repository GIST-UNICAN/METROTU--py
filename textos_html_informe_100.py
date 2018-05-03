apartado_informe=""" <!doctype html>
<div style='border:none;border-bottom:solid windowtext 1.5pt;padding:0cm 0cm 1.0pt 0cm'>

<p class=MsoNormal align=center style='text-align:center;border:none;
padding:0cm'><span style='font-size:16.0pt;line-height:106%'>&nbsp;</span></p>

</div>

<p class=MsoNormal align=center style='text-align:center'><span
style='font-size:16.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal align=center style='text-align:center'><b><span
style='font-size:16.0pt;line-height:106%'>{titulo}</span></b></p>

<p class=MsoNormal><u><span style='font-size:12.0pt;line-height:106%'>Gráfico evolución:</span></u></p>

<div class=imagen><img align="middle", src="{grafico}"></div>

<p class=MsoNormal style='border:none;padding:0cm'><span style='font-size:12.0pt;
line-height:106%'>&nbsp;</span></p>

</div>"""

apartado_informe_tabla=""" <!doctype html>
<div style='border:none;border-bottom:solid windowtext 1.5pt;padding:0cm 0cm 1.0pt 0cm'>

<p class=MsoNormal align=center style='text-align:center;border:none;
padding:0cm'><span style='font-size:16.0pt;line-height:106%'>&nbsp;</span></p>

</div>

<p class=MsoNormal align=center style='text-align:center'><span
style='font-size:16.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal align=center style='text-align:center'><b><span
style='font-size:16.0pt;line-height:106%'>Tabla resumen velocidades y tiempos</span></b></p>

<p class=MsoNormal><span style='font-size:12.0pt;line-height:106%;text-align:center'>{tabla}</span></p>

<p class=MsoNormal style='border:none;padding:0cm'><span style='font-size:12.0pt;
line-height:106%'>&nbsp;</span></p>

</div>"""

plantilla_web_estilos="""<!doctype html>
<html>

<head>
<meta http-equiv=Content-Type content="text/html; charset=windows-1252">
<meta name=Generator content="Microsoft Word 15 (filtered)">
<style>
<!--
 /* Font Definitions */
 @font-face
	{font-family:"Cambria Math";
	panose-1:2 4 5 3 5 4 6 3 2 4;}
@font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
 /* Style Definitions */
 p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:8.0pt;
	margin-left:0cm;
	line-height:106%;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.msonormal0, li.msonormal0, div.msonormal0
	{mso-style-name:msonormal;
	margin-right:0cm;
	margin-left:0cm;
	font-size:12.0pt;
	font-family:"Times New Roman",serif;}
.MsoChpDefault
	{font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
@page WordSection1
	{size:595.3pt 841.9pt;
	margin:70.85pt 3.0cm 70.85pt 3.0cm;}
div.WordSection1
	{page:WordSection1;}
-->
</style>
<link rel="stylesheet" type="text/css" href="tabla.css"  />
</head>

<body lang=ES style="margin:0; padding:0;">

<div class=WordSection1>
"""

plantilla_web_cuerpo="""<p class=MsoNormal align=center style='text-align:center'><span
style='font-size:16.0pt;line-height:106%'>INFORME LÍNEA CENTRAL SEMANA {dia_inicio} de {mes_inicio} al {dia_fin} de {mes_fin}</span></p>

{informe_completo}

<p class=MsoNormal align=center style='text-align:center'><span
style='font-size:12.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal><span style='font-size:12.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal><span style='font-size:12.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal><span style='font-size:12.0pt;line-height:106%'>&nbsp;</span></p>

<p class=MsoNormal>&nbsp;</p>

</div>

</body>"""