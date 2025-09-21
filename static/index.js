// deezerAPI = (calltype, id) => { return `https://api.deezer.com/${calltype}/${id}` }

data = {}

lookup = async(endpoint) => {
    deezerID = document.getElementById(`${endpoint}IDInput`).value
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
    document.getElementById('available').value = data.availability.all
    document.getElementById('partiallyAvailable').value = data.availability.some
    document.getElementById('unavailable').value = data.availability.none
    document.getElementById('trackList').innerHTML = `
        <thead>
            <tr>
                <th>Track</th>
                <th>Title</th>
                <th>Artists</th>
                <th>Length</th>
                <th>Version</th>
                <th>Year</th>
                <th>Label</th>
                <th>Release Date</th>
                <th>Recording</th>
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

copyContent = (caller) => { navigator.clipboard.writeText(caller.value) }

document.addEventListener('DOMContentLoaded', () => {
    ['album', 'track'].forEach((endpoint) => {
        document.getElementById(`${endpoint}IDInput`).addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                document.getElementById(`${endpoint}LookupButton`).click()
            }
        })
    })
})