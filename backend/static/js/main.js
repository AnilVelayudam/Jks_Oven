// CART POPUP
function showCartPopup(){
    const popup = document.getElementById("cart-popup");
    popup.classList.add("show");

    setTimeout(() => {
        popup.classList.remove("show");
    }, 2000);
}


// SEARCH
const input = document.getElementById("search-input");
const resultsBox = document.getElementById("search-results");

if(input){
input.addEventListener("keyup", function(){

let query = input.value;

if(query.length < 1){
resultsBox.style.display = "none";
return;
}

fetch(`/search-products/?q=${query}`)
.then(res => res.json())
.then(data => {

resultsBox.innerHTML = "";

if(data.length === 0){
resultsBox.innerHTML = "<div class='search-item'>No products found</div>";
resultsBox.style.display = "block";
return;
}

data.forEach(product => {

let item = document.createElement("div");

item.classList.add("search-item");

item.innerHTML = `
<img src="${product.image}">
<div>
<div class="search-name">${product.name}</div>
<div class="search-price">₹${product.price}</div>
</div>
`;

item.onclick = () => {
window.location.href = `/product/${product.id}/`;
};

resultsBox.appendChild(item);

});

resultsBox.style.display = "block";

});

});
}


// ADD TO CART (BUTTON)
document.addEventListener("DOMContentLoaded", function(){

document.querySelectorAll(".add-to-cart-btn").forEach(btn => {

btn.addEventListener("click", function(){

let productId = this.dataset.id;

fetch(`/add-to-cart/${productId}/`)
.then(() => {

showCartPopup();

let count = document.querySelector(".cart-count");

if(count.innerText){
count.innerText = parseInt(count.innerText) + 1;
} else {
count.innerText = 1;
}

});

});

});

});


document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".hero-slide");

    // SET BACKGROUND IMAGES
    slides.forEach(slide => {
        const bg = slide.getAttribute("data-bg");
        if (bg) {
            slide.style.backgroundImage = `url(${bg})`;
        }
    });

    // SLIDER
    let index = 0;

    setInterval(() => {
        slides[index].classList.remove("active");

        index = (index + 1) % slides.length;

        slides[index].classList.add("active");
    }, 3000);

});