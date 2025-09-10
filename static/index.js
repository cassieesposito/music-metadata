// deezerAPI = (calltype, id) => { return `https://api.deezer.com/${calltype}/${id}` }

lookup = async(endpoint) => {
    deezerID = document.getElementById(`${endpoint}ID`).value
    res = await fetch(`/${endpoint}?` + new URLSearchParams({ deezerID: deezerID }))
    data = await res.json()
    console.log(data)
    displayData(data)
}

displayData = (data) => {
    document.getElementById('title').innerHTML = `<a href="${data.albumLink}">${data.title}</a>`
    document.getElementById('artist').innerHTML = `<a href="${data.artistLink}">${data.artist}</a>`
    document.getElementById('deezerReleaseDate').innerHTML = data.deezerReleaseDate
    document.getElementById('upc').innerHTML = `<a href="https://isrc.soundexchange.com/?tab=%22code%22&icpnCode=%22${data.upc}%22&showReleases=true">${data.upc}</a>`
    document.getElementById('label').innerHTML = data.label

    document.getElementById('trackList').innerHTML = `
            <tr>
                <td>Track</td>
                <td>Title</td>
                <td>Artists</td>
                <td>Length</td>
                <td>Version</td>
                <td>Year</td>
                <td>Label</td>
                <td>Release Date</td>
            </tr>`


    data.tracks.forEach((track, index) => {
        trackList = document.getElementById('trackList')
        trackList.innerHTML += `<tr>    
                                    <td>${index+1}</td>
                                    <td><a href="https://isrc.soundexchange.com/?tab=%22code%22&isrcCode=%22${track.dz.isrc}%22&showReleases=true">${track.sx.title}</a></td>
                                    <td>${track.dz.artists}</td>
                                    <td>${track.dz.length}</td>
                                    <td>${track.sx.version}</td>
                                    <td>${track.sx.year}</td>
                                    <td>${track.sx.label.toString().replace('/','<br>')}</td>
                                    <td>${track.sx.date}</td>
                                </tr>`
    });

}