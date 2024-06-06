function replacePdfAndImage() {
    for (const item of Deno.readDirSync("_publications")) {
        console.log(item.name)
        const name = item.name.replace(/\.md$/, "");
        const pdfPath = `files/${name}.pdf`
        const imagePath = `images/publications/${name}.jpg`
        const oldContent = Deno.readTextFileSync(`_publications/${item.name}`)
        let newContent = oldContent.replaceAll(/paperurl: "(.*)"/g, `paperurl: "/${pdfPath}"`)
        newContent = newContent.replaceAll(/poster:\s*$/gm, `poster: /${imagePath}\n`)
        Deno.writeTextFileSync(`_publications/${item.name}`, newContent)
    }
}

replacePdfAndImage()