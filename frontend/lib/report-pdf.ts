// A4 in PDF points; the report is laid out 794px wide, A4's width at 96 dpi.
const PAGE_WIDTH = 595.28
const PAGE_HEIGHT = 841.89

/** The report element as an A4 PDF: a sharp picture of it. On one page, scaled down when it's
 * taller (a candidate's report); or, with `pages`, at full width over as many pages as it takes
 * (every candidate of a test). The libraries load only when a report is made. */
export async function reportPdf(
  node: HTMLElement,
  name: string,
  pages = false
): Promise<File> {
  const [{ toJpeg }, { jsPDF }] = await Promise.all([
    import("html-to-image"),
    import("jspdf"),
  ])
  // The copy is drawn in place, not off screen where the page keeps the report.
  // JPEG keeps the file small enough to send in a chat or an email.
  const image = await toJpeg(node, {
    pixelRatio: 2,
    quality: 0.9,
    backgroundColor: "#ffffff",
    style: { position: "static", left: "auto" },
  })
  const scale = pages
    ? PAGE_WIDTH / node.offsetWidth
    : Math.min(PAGE_WIDTH / node.offsetWidth, PAGE_HEIGHT / node.offsetHeight)
  const width = node.offsetWidth * scale
  const height = node.offsetHeight * scale
  const pdf = new jsPDF({ unit: "pt", format: "a4" })
  const count = pages ? Math.ceil(height / PAGE_HEIGHT) : 1

  // Each page shows the next page-high slice of the same picture.
  for (let page = 0; page < count; page++) {
    if (page > 0) {
      pdf.addPage()
    }

    pdf.addImage(
      image,
      "JPEG",
      (PAGE_WIDTH - width) / 2,
      -page * PAGE_HEIGHT,
      width,
      height
    )
  }

  return new File([pdf.output("blob")], name, { type: "application/pdf" })
}
