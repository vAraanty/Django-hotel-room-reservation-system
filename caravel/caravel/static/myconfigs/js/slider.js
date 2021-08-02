var currentSlide = 1;
showSlides(currentSlide);

function moveSlide(n) {
	showSlides(currentSlide += n);
}

function setSlide(n) {
	showSlides(currentSlide = n);
}

function showSlides(n) {
	var slides = document.getElementsByClassName("slide");
	var dots = document.getElementsByClassName("dot");
	if (n > slides.length){
	  currentSlide = 1;
	}
	if(n < 1){
		currentSlide = slides.length;
	}
	for (let i = 0; i < slides.length; i++){
      slides[i].classList.add("invisible");
	}
	for (let i = 0; i < dots.length; i++) {
      dots[i].classList.remove("active");
	}
	slides[currentSlide-1].classList.remove("invisible");
	dots[currentSlide-1].classList.add("active");
}