
document.addEventListener("DOMContentLoaded", function () {

    const AutoComplete = document.querySelector(".search ul")
    const acInput = document.querySelector(".search input")
    const log = document.querySelector(".activity")
    const logClass = ["name-div", "name-div", "time-div", "menu-div", "overlay"]
    let lastKw = ""

    // Loading Screen //
    const showLoading = () => {
        const main = this.querySelector(".safezone");
        const bg = main.appendChild(this.createElement("div"));
        bg.className = "loading";
        let load = this.createElement("div");
        load.className = "loadBar";
        const title = this.createElement("h1");
        title.textContent = "데이터 가져오는 중";
        const prog = this.createElement("div");
        prog.className = "progress";
        bg.appendChild(title);
        load = bg.appendChild(load);
        return load.appendChild(prog);
    }; // Show Loading screen //
    const updateProgress = (percent) => {
        let progress = this.querySelector(".progress") || showLoading();
        progress.style["width"] = `${percent.toString()}%`;
        if (percent >= 100) {
            let loading = this.querySelector(".loading");
            if (loading) {
                loading.remove();
            }
        }
    }; // Update Loading screen //
    const toastDone = (div) => {
        div.remove()
    }
    const toast = (msg) => {
        let div = document.createElement("div"), span = document.createElement("span")
        div.className = "toast"
        span.innerHTML = msg
        div.appendChild(span)
        div = document.querySelector("body").appendChild(div)
        setTimeout(toastDone, 5000, div)
    }
    const acClear = () => {
        AutoComplete.innerHTML = ""
    }
    const acItems = (tag_obj) => {
        let li = document.createElement("li")
        var items = []
        for (let i = 0; i < 3; i++) {
            var div = document.createElement("div")
            div.className = "main"
            items.push(div)
        }
        items[0].innerHTML = tag_obj.num + "번"
        items[1].innerHTML = tag_obj.name
        items[2].innerHTML = tag_obj.time
        items.forEach(element => {
            li.appendChild(element)
        })
        var menuEl = document.createElement("div")
        menuEl.className = "optional"
        menuEl.innerHTML = tag_obj.menu
        li.appendChild(menuEl)
        li.addEventListener("click", async () => {
            await tagUser(tag_obj.num)
            acInput.value = ""
            acClear()
        })
        return li
    }
    const acData = async (kw) => {
        let load = []
        const response = await fetch(`api/search?kw=${kw}`)
        if (response.ok) {
            const data = await response.json()
            data.result.forEach((obj) => {
                load.push(acItems(obj))
            })
            if (!load.length) {
                acClear()
            }
            else {
                await acLoad(kw, load)
            }
        }



    }
    const acLoad = async (kw, load) => {
        let current = () => { return acInput.value }
        for (let i = 0; i < load.length; i++) {
            if (current() == kw) {
                if (i == 0) {
                    acClear()
                }
                AutoComplete.appendChild(load[i])
            }
            else {
                if (!current()) {
                    acClear()
                }
                i = load.length
            }
        }

    }
    const cancelUser = async (kw) => {
        let li
        const response = await fetch(`api/cancel?data=${kw}`)
        if (!response.ok) {
            return toast("미이용 이용자 입니다!!")
        }
        const data = await response.json()
        li = document.querySelector(`.${data.name}`).parentElement
        li.remove()
        await updateCount()
        return toast(`${data.num} 번 ${data.name} 이용 취소`)
    }
    const menuChange = async (kw) => {
        let li
        const response = await fetch(`api/menu?data=${kw}`)
        if (!response.ok) {
            return toast("미이용 이용자 입니다!!")
        }
        const data = await response.json()
        li = document.querySelector(`.${data.name}`).parentElement
        li = li.querySelector("span")
        li.innerHTML = data.menu
        await updateCount()
        return toast(`${data.num} 번 ${data.name} 메뉴 변경`)
    }
    const updateCount = async () => {
        const response = await fetch("api/count")
        if (!response.ok)
            return toast("이용자 수 불러오기 실패")
        const data = await response.json()
        let counterDiv = document.querySelectorAll(".counter-item")
        counterDiv[0].innerHTML = `<span>전체 이용자</span><span>${data.total} 명</span>`
        counterDiv[1].innerHTML = `<span>죽식 이용자</span><span>${data.menu} 명</span>`
    }
    const tagUser = async (kw) => {
        let li
        const response = await fetch(`api/?data=${kw}`)
        if (!response.ok) {
            return toast(`존재하지 않는 이용자 입니다!!! ${kw}`)
        }
        const data = await response.json()
        if (data.exists == 0) {
            log.prepend(logItems(data))
        }
        li = document.querySelector(`.${data.name}`)
        li.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" })
        toast(`${data.num}번 ${data.name} 입력`)
        await updateCount()
    }
    const logItems = (tag_obj) => {
        let li = document.createElement("li")
        var items = []
        for (let i = 0; i < 4; i++) {
            var div = document.createElement("div")
            div.className = logClass[i]
            items.push(div)
        }
        items[0].innerHTML = tag_obj.num + "번"
        items[0].classList.add(tag_obj.num)
        items[1].innerHTML = tag_obj.name
        items[1].classList.add(tag_obj.name)
        items[2].innerHTML = tag_obj.time
        var buttons = [document.createElement("span"), document.createElement("button"), document.createElement("button")]
        buttons[0].innerHTML = tag_obj.menu
        buttons[1].innerHTML = "이용취소"
        buttons[1].addEventListener("click", async () => {
            await cancelUser(tag_obj.num)
        })
        buttons[2].innerHTML = "메뉴변경"
        buttons[2].addEventListener("click", async () => {
            await menuChange(tag_obj.num)
        })
        buttons.forEach((element) => {
            items[3].appendChild(element)
        })
        items.forEach((element) => {
            li.appendChild(element)
        })
        return li
    }
    const load = async () => {
        updateProgress(0)
        const response = await fetch("api/init")
        if (!response.ok) {
            return toast("오류 발생: 새로고침 이후에도 지속될 시 프로그램 재시작")
        }
        updateProgress(80)
        const data = await response.json()
        for (let i = 0; i < data.result.length; i++) {
            log.appendChild(logItems(data.result[i]))
        }
        await updateCount()
        updateProgress(100)

    }
    const start = () => {
        load().then(() => {
            return
        })
    }
    // Serial card reader //
    let port;
    let reader;
    let readerOut = "";
    const readerBtn = this.querySelector(".readerBtn");
    const readerStatus = this.querySelector(".readerStatus");
    const readData = async () => {
        const decoder = new TextDecoder();
        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    console.log("Stream closed");
                    reader.releaseLock();
                    break;
                }
                if (value) {
                    const out_char = decoder.decode(value, { stream: true });
                    var out = Array.from(out_char);
                    for (let i = 0; i < out.length; i++) {
                        if (/^[a-z0-9]+$/i.test(out[i])) {
                            readerOut += out[i];
                        } else {
                            if (readerOut != "") {
                                console.log(`RFID data: ${readerOut}`);
                                await tagUser(readerOut);
                            }
                            readerOut = "";
                        }
                    }
                }
            }
        } catch (error) {
            console.error(`Failed to read card data: ${error}`);
        }
    }; // Parse raw data from serial device //
    const initReader = async () => {
        if (reader) {
            if (readerStatus.classList.contains("connected")) {
                readerStatus.classList.remove("connected");
            }
            reader.cancel();
            reader = null;
        }
        if (port) {
            port.forget();
        }
        try {
            port = await navigator.serial.requestPort();
            await port.open({ baudRate: 9600 });
            reader = port.readable.getReader();
            readerStatus.classList.add("connected");

            readData();
            port.addEventListener("disconnect", () => {
                if (readerStatus.classList.contains("connected")) {
                    readerStatus.classList.remove("connected");

                }
            });
        } catch (error) {
            console.error("Failed to connect to RFID reader:", error);
            if (readerStatus.classList.contains("connected")) {
                readerStatus.classList.remove("connected");
            }
            if (port) {
                port.forget();
            }
        }
    }; // Select serial device and start reading data //

    start()
    // check webSerial api compatibility //
    if ("serial" in navigator) {
        // Click to set up reader //
        readerBtn.addEventListener("click", initReader);
        readerStatus.innerHTML="█████"
    } else {
        // Unsupported browser //
        readerBtn.innerHTML = "미호환 브라우저";
        readerStatus.innerHTML="▝▞▞▞▞▖"
    }
    acInput.addEventListener("keyup", async (e) => {
        const kw = acInput.value
        if (kw && lastKw !== kw) {
            lastKw = String(kw)
            await acData(kw)
        }
        else {
            if (!kw) {
                lastKw = ""
                acClear()
            }
        }
        if (e.key === "Enter") {
            await tagUser(kw)
            lastKw = ""
            acInput.value = ""
            acClear()
        }

    })

})