"""Small deterministic SVG line chart for the tabulated range model (standard library)."""
import html
import math


def chart(title, ylabel, curves, ticks, thresholds=()):
    left, right, top, bottom = 94, 740, 62, 326
    def xp(x):
        return left+(right-left)*(x-5)/300
    def yp(y):
        return bottom-(bottom-top)*math.log(y/ticks[0])/math.log(ticks[-1]/ticks[0])
    def label(x,y,s,anchor="middle",size=13):
        return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}">{html.escape(s)}</text>'
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 414" role="img">',
             '<title>'+html.escape(title)+'</title>',
             '<rect width="800" height="414" fill="#fff"/>',
             '<g font-family="system-ui,sans-serif" fill="#1e313b">',
             label(left,27,title,"start",20),label(left,49,ylabel,"start")]
    for y in ticks:
        lines += [f'<path d="M{left} {yp(y):.1f}H{right}" stroke="#dce1e5"/>',
                  label(left-8,yp(y)+4,f"{y:g}","end")]
    for x in (10,50,100,150,225,305):
        lines.append(label(xp(x),348,str(x)))
    lines += [label((left+right)/2,372,"Antenna-plane separation (mm)"),
              f'<defs><clipPath id="plot"><rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"/></clipPath></defs>',
              '<g clip-path="url(#plot)">']
    for t in thresholds:
        lines.append(f'<path d="M{left} {yp(t):.1f}H{right}" stroke="#79858a" stroke-dasharray="4 4"/>')
    colors = ["#16668c","#bb4c26","#387b4b","#754e96"]
    for (_,points),color in zip(curves,colors):
        points = " ".join(f"{xp(x):.2f},{yp(y):.2f}" for x,y in points if y>0)
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.8"/>')
    lines.append('</g>')
    for i,((name,_),color) in enumerate(zip(curves,colors)):
        x = left + i*158
        lines += [f'<path d="M{x} 397h20" stroke="{color}" stroke-width="3"/>',label(x+25,401,name,"start")]
    return "\n".join(lines+["</g></svg>",""])
