// deezerAPI = (calltype, id) => { return `https://api.deezer.com/${calltype}/${id}` }

data = {}

lookup = async(endpoint) => {
    deezerID = document.getElementById(`${endpoint}ID`).value
    res = await fetch(`/${endpoint}?` + new URLSearchParams({ deezerID: deezerID }))
    data = await res.json()
    console.log(data)
    displayData()
}

displayData = () => {
    document.getElementById('title').innerHTML = `<a href="${data.albumLink}">${data.title}</a>`
    document.getElementById('artist').innerHTML = `<a href="${data.artistLink}">${data.artist}</a>`
    document.getElementById('deezerReleaseDate').innerHTML = data.deezerReleaseDate
    document.getElementById('upc').innerHTML = `<a href="https://isrc.soundexchange.com/?tab=%22code%22&icpnCode=%22${data.upc}%22&showReleases=true">${data.upc}</a>`
    document.getElementById('label').innerHTML = data.label

    document.getElementById('trackList').innerHTML = `
        <thead>
            <tr>
                <td>Track</td>
                <td>Title</td>
                <td>Artists</td>
                <td>Length</td>
                <td>Version</td>
                <td>Year</td>
                <td>Label</td>
                <td>Release Date</td>
                <td>Recording</td>
            </tr>
        </thead>
        <tbody id="trackListBody">
        </tbody>`


    data.tracks.forEach((track, index) => {
        trackListBody = document.getElementById('trackListBody')
        trackListBody.innerHTML += `
            <tr id="track${index}">    
                <td>${index+1}</td>
                <td id="sxTitle${index}"></td>
                <td>${track.dz.artists}</td>
                <td>${track.dz.length}</td>
                <td id="sxVersion${index}"></td>
                <td id="sxYear${index}"></td>
                <td id="sxLabel${index}"></td>
                <td id="sxDate${index}"></td>
                <td>
                    <select id="recording${index}" style="visibility:hidden;" onchange="fillTrack(${index})">
                    </select>
                </td>
            </tr>`

        if (track.sx.title.length > 1) { document.getElementById(`recording${index}`).style.visibility = "visible" }
        Array.from(Array(track.sx.title.length).keys()).forEach((e) => {
            document.getElementById(`recording${(index)}`).innerHTML += `<option value="${e}">${e}</option>`
        }, { index: index })
        fillTrack(index)
    })

}

fillTrack = (index) => {
    recording = document.getElementById(`recording${index}`).value
    track = data.tracks[index]

    document.getElementById(`sxTitle${index}`).innerHTML = `
        <a href="https://isrc.soundexchange.com/?tab=%22code%22&isrcCode=%22${track.dz.isrc[recording]}%22&showReleases=true">
            ${track.sx.title[recording]}
        </a>`

    document.getElementById(`sxVersion${index}`).innerHTML = track.sx.version[recording]
    document.getElementById(`sxYear${index}`).innerHTML = track.sx.year[recording]
    document.getElementById(`sxLabel${index}`).innerHTML = track.sx.label[recording] ?
        track.sx.label[recording].toString().replace('/', '<br>') : null

    document.getElementById(`sxDate${index}`).innerHTML = track.sx.date[recording]
}