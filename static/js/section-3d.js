// 3D scroll effect – toggle .in-view when section enters viewport
(function(){
  const sections = document.querySelectorAll('.section-3d');
  if(!sections.length) return;
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('in-view');
      }else{
        entry.target.classList.remove('in-view');
      }
    });
  },{threshold:0.3});
  sections.forEach(sec=>observer.observe(sec));
})();