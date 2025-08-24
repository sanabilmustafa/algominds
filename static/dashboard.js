const pnValue = document.getElementsByClassName("pn-value, change");
for (let el of pnValue) {
    console.log("hello")
    const value = parseFloat(el.innerText);
    console.log(value);
    if (value > 0) {
      el.classList.add("green");
      pnIndexValue[0].classList.add("green");
    } else if (value < 0) {
      el.classList.add("red");
      pnIndexValue[0].classList.add("red");
    }
  }