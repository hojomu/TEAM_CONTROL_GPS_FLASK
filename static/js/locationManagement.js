/**
 * 
 */

// 카카오맵 설정
var container = document.getElementById('map'); //지도를 담을 영역의 DOM 레퍼런스
var options = { //지도를 생성할 때 필요한 기본 옵션
	center: new kakao.maps.LatLng(35.53942967185377, 129.33628189825467), //지도의 중심좌표.
	level: 3 //지도의 레벨(확대, 축소 정도)
};

// 집중 환자 마커 이미지
var focusedImageSrc = "https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png";

let intervalFocus;

//마커 리 랜더링을 위해 배열 생성
markers = [];


// 툴팁 마커 설정 시작
/**
 * AbstractOverlay를 상속받을 객체를 선언합니다.
 */
function TooltipMarker(position, tooltipText) {
    this.position = position;
    var node = this.node = document.createElement('div');
    node.className = 'node';

    var tooltip = document.createElement('div');
    tooltip.className = 'tooltip',

    tooltip.appendChild(document.createTextNode(tooltipText));
    node.appendChild(tooltip);
    
    // 툴팁 엘리먼트에 마우스 인터렉션에 따라 보임/숨김 기능을 하도록 이벤트를 등록합니다.
    node.onmouseover = function() {
        tooltip.style.display = 'block';
    };
    node.onmouseout = function() {
        tooltip.style.display = 'none';
    };
}

// AbstractOverlay 상속. 프로토타입 체인을 연결합니다.
TooltipMarker.prototype = new kakao.maps.AbstractOverlay;

// AbstractOverlay의 필수 구현 메소드.
// setMap(map)을 호출했을 경우에 수행됩니다.
// AbstractOverlay의 getPanels() 메소드로 MapPanel 객체를 가져오고
// 거기에서 오버레이 레이어를 얻어 생성자에서 만든 엘리먼트를 자식 노드로 넣어줍니다.
TooltipMarker.prototype.onAdd = function() {
    var panel = this.getPanels().overlayLayer;
    panel.appendChild(this.node);
};

// AbstractOverlay의 필수 구현 메소드.
// setMap(null)을 호출했을 경우에 수행됩니다.
// 생성자에서 만든 엘리먼트를 오버레이 레이어에서 제거합니다.
TooltipMarker.prototype.onRemove = function() {
    this.node.parentNode.removeChild(this.node);
};

// AbstractOverlay의 필수 구현 메소드.
// 지도의 속성 값들이 변화할 때마다 호출됩니다. (zoom, center, mapType)
// 엘리먼트의 위치를 재조정 해 주어야 합니다.
TooltipMarker.prototype.draw = function() {
    // 화면 좌표와 지도의 좌표를 매핑시켜주는 projection객체
    var projection = this.getProjection();
    
    // overlayLayer는 지도와 함께 움직이는 layer이므로
    // 지도 내부의 위치를 반영해주는 pointFromCoords를 사용합니다.
    var point = projection.pointFromCoords(this.position);

    // 내부 엘리먼트의 크기를 얻어서
    var width = this.node.offsetWidth;
    var height = this.node.offsetHeight;

    // 해당 위치의 정중앙에 위치하도록 top, left를 지정합니다.
    this.node.style.left = (point.x - width/2) + "px";
    this.node.style.top = (point.y - height/2) + "px";
};

// 좌표를 반환하는 메소드
TooltipMarker.prototype.getPosition = function() {
    return this.position;
};

/**
 * 지도 영역 외부에 존재하는 마커를 추적하는 기능을 가진 객체입니다.
 * 클리핑 알고리즘을 사용하여 tracker의 좌표를 구하고 있습니다.
 */
function MarkerTracker(map, target) {
    // 클리핑을 위한 outcode
    var OUTCODE = {
        INSIDE: 0, // 0b0000
        TOP: 8, //0b1000
        RIGHT: 2, // 0b0010
        BOTTOM: 4, // 0b0100
        LEFT: 1 // 0b0001
    };
    
    // viewport 영역을 구하기 위한 buffer값
    // target의 크기가 60x60 이므로 
    // 여기서는 지도 bounds에서 상하좌우 30px의 여분을 가진 bounds를 구하기 위해 사용합니다.
    var BOUNDS_BUFFER = 30;
    
    // 클리핑 알고리즘으로 tracker의 좌표를 구하기 위한 buffer값
    // 지도 bounds를 기준으로 상하좌우 buffer값 만큼 축소한 내부 사각형을 구하게 됩니다.
    // 그리고 그 사각형으로 target위치와 지도 중심 사이의 선을 클리핑 합니다.
    // 여기서는 tracker의 크기를 고려하여 40px로 잡습니다.
    var CLIP_BUFFER = 40;

    // trakcer 엘리먼트
    var tracker = document.createElement('div');
    tracker.className = 'tracker';

    // 내부 아이콘
    var icon = document.createElement('div');
    icon.className = 'icon';

    // 외부에 있는 target의 위치에 따라 회전하는 말풍선 모양의 엘리먼트
    var balloon = document.createElement('div');
    balloon.className = 'balloon';

    tracker.appendChild(balloon);
    tracker.appendChild(icon);

    map.getNode().appendChild(tracker);

    // traker를 클릭하면 target의 위치를 지도 중심으로 지정합니다.
    tracker.onclick = function() {
        map.setCenter(target.getPosition());
        setVisible(false);
    };

    // target의 위치를 추적하는 함수
    function tracking() {
        var proj = map.getProjection();
        
        // 지도의 영역을 구합니다.
        var bounds = map.getBounds();
        
        // 지도의 영역을 기준으로 확장된 영역을 구합니다.
        var extBounds = extendBounds(bounds, proj);

        // target이 확장된 영역에 속하는지 판단하고
        if (extBounds.contain(target.getPosition())) {
            // 속하면 tracker를 숨깁니다.
            setVisible(false);
        } else {
            // target이 영역 밖에 있으면 계산을 시작합니다.
            

            // 지도 bounds를 기준으로 클리핑할 top, right, bottom, left를 재계산합니다.
            //
            //  +-------------------------+
            //  | Map Bounds              |
            //  |   +-----------------+   |
            //  |   | Clipping Rect   |   |
            //  |   |                 |   |
            //  |   |        *       (A)  |     A
            //  |   |                 |   |
            //  |   |                 |   |
            //  |   +----(B)---------(C)  |
            //  |                         |
            //  +-------------------------+
            //
            //        B
            //
            //                                       C
            // * 은 지도의 중심,
            // A, B, C가 TooltipMarker의 위치,
            // (A), (B), (C)는 각 TooltipMarker에 대응하는 tracker입니다.
            // 지도 중심과 각 TooltipMarker를 연결하는 선분이 있다고 가정할 때,
            // 그 선분과 Clipping Rect와 만나는 지점의 좌표를 구해서
            // tracker의 위치(top, left)값을 지정해주려고 합니다.
            // tracker 자체의 크기가 있기 때문에 원래 지도 영역보다 안쪽의 가상 영역을 그려
            // 클리핑된 지점을 tracker의 위치로 사용합니다.
            // 실제 tracker의 position은 화면 좌표가 될 것이므로 
            // 계산을 위해 좌표 변환 메소드를 사용하여 모두 화면 좌표로 변환시킵니다.
            
            // TooltipMarker의 위치
            var pos = proj.containerPointFromCoords(target.getPosition());
            
            // 지도 중심의 위치
            var center = proj.containerPointFromCoords(map.getCenter());

            // 현재 보이는 지도의 영역의 남서쪽 화면 좌표
            var sw = proj.containerPointFromCoords(bounds.getSouthWest());
            
            // 현재 보이는 지도의 영역의 북동쪽 화면 좌표
            var ne = proj.containerPointFromCoords(bounds.getNorthEast());
            
            // 클리핑할 가상의 내부 영역을 만듭니다.
            var top = ne.y + CLIP_BUFFER;
            var right = ne.x - CLIP_BUFFER;
            var bottom = sw.y - CLIP_BUFFER;
            var left = sw.x + CLIP_BUFFER;

            // 계산된 모든 좌표를 클리핑 로직에 넣어 좌표를 얻습니다.
            var clipPosition = getClipPosition(top, right, bottom, left, center, pos);
            
            // 클리핑된 좌표를 tracker의 위치로 사용합니다.
            tracker.style.top = clipPosition.y + 'px';
            tracker.style.left = clipPosition.x + 'px';

            // 말풍선의 회전각을 얻습니다.
            var angle = getAngle(center, pos);
            
            // 회전각을 CSS transform을 사용하여 지정합니다.
            // 브라우저 종류에따라 표현되지 않을 수도 있습니다.
            // https://caniuse.com/#feat=transforms2d
            balloon.style.cssText +=
                '-ms-transform: rotate(' + angle + 'deg);' +
                '-webkit-transform: rotate(' + angle + 'deg);' +
                'transform: rotate(' + angle + 'deg);';

            // target이 영역 밖에 있을 경우 tracker를 노출합니다.
            setVisible(true);
        }
    }

    // 상하좌우로 BOUNDS_BUFFER(30px)만큼 bounds를 확장 하는 함수
    //
    //  +-----------------------------+
    //  |              ^              |
    //  |              |              |
    //  |     +-----------------+     |
    //  |     |                 |     |
    //  |     |                 |     |
    //  |  <- |    Map Bounds   | ->  |
    //  |     |                 |     |
    //  |     |                 |     |
    //  |     +-----------------+     |
    //  |              |              |
    //  |              v              |
    //  +-----------------------------+
    //  
    // 여기서는 TooltipMaker가 완전히 안보이게 되는 시점의 영역을 구하기 위해서 사용됩니다.
    // TooltipMarker는 60x60 의 크기를 가지고 있기 때문에 
    // 지도에서 완전히 사라지려면 지도 영역을 상하좌우 30px만큼 더 드래그해야 합니다.
    // 이 함수는 현재 보이는 지도 bounds에서 상하좌우 30px만큼 확장한 bounds를 리턴합니다.
    // 이 확장된 영역은 TooltipMarker가 화면에서 보이는지를 판단하는 영역으로 사용됩니다.
    function extendBounds(bounds, proj) {
        // 주어진 bounds는 지도 좌표 정보로 표현되어 있습니다.
        // 이것을 BOUNDS_BUFFER 픽셀 만큼 확장하기 위해서는
        // 픽셀 단위인 화면 좌표로 변환해야 합니다.
        var sw = proj.pointFromCoords(bounds.getSouthWest());
        var ne = proj.pointFromCoords(bounds.getNorthEast());

        // 확장을 위해 각 좌표에 BOUNDS_BUFFER가 가진 수치만큼 더하거나 빼줍니다.
        sw.x -= BOUNDS_BUFFER;
        sw.y += BOUNDS_BUFFER;

        ne.x += BOUNDS_BUFFER;
        ne.y -= BOUNDS_BUFFER;

        // 그리고나서 다시 지도 좌표로 변환한 extBounds를 리턴합니다.
        // extBounds는 기존의 bounds에서 상하좌우 30px만큼 확장된 영역 객체입니다.  
        return new kakao.maps.LatLngBounds(
                        proj.coordsFromPoint(sw),proj.coordsFromPoint(ne));
        
    }


    // Cohen–Sutherland clipping algorithm
    // 자세한 내용은 아래 위키에서...
    // https://en.wikipedia.org/wiki/Cohen%E2%80%93Sutherland_algorithm
    function getClipPosition(top, right, bottom, left, inner, outer) {
        function calcOutcode(x, y) {
            var outcode = OUTCODE.INSIDE;

            if (x < left) {
                outcode |= OUTCODE.LEFT;
            } else if (x > right) {
                outcode |= OUTCODE.RIGHT;
            }

            if (y < top) {
                outcode |= OUTCODE.TOP;
            } else if (y > bottom) {
                outcode |= OUTCODE.BOTTOM;
            }

            return outcode;
        }

        var ix = inner.x;
        var iy = inner.y;
        var ox = outer.x;
        var oy = outer.y;

        var code = calcOutcode(ox, oy);

        while(true) {
            if (!code) {
                break;
            }

            if (code & OUTCODE.TOP) {
                ox = ox + (ix - ox) / (iy - oy) * (top - oy);
                oy = top;
            } else if (code & OUTCODE.RIGHT) {
                oy = oy + (iy - oy) / (ix - ox) * (right - ox);        
                ox = right;
            } else if (code & OUTCODE.BOTTOM) {
                ox = ox + (ix - ox) / (iy - oy) * (bottom - oy);
                oy = bottom;
            } else if (code & OUTCODE.LEFT) {
                oy = oy + (iy - oy) / (ix - ox) * (left - ox);     
                ox = left;
            }

            code = calcOutcode(ox, oy);
        }

        return {x: ox, y: oy};
    }

    // 말풍선의 회전각을 구하기 위한 함수
    // 말풍선의 anchor가 TooltipMarker가 있는 방향을 바라보도록 회전시킬 각을 구합니다.
    function getAngle(center, target) {
        var dx = target.x - center.x;
        var dy = center.y - target.y ;
        var deg = Math.atan2( dy , dx ) * 180 / Math.PI; 

        return ((-deg + 360) % 360 | 0) + 90;
    }
    
    // tracker의 보임/숨김을 지정하는 함수
    function setVisible(visible) {
        tracker.style.display = visible ? 'block' : 'none';
    }
    
    // Map 객체의 'zoom_start' 이벤트 핸들러
    function hideTracker() {
        setVisible(false);
    }
    
    // target의 추적을 실행합니다.
    this.run = function() {
        kakao.maps.event.addListener(map, 'zoom_start', hideTracker);
        kakao.maps.event.addListener(map, 'zoom_changed', tracking);
        kakao.maps.event.addListener(map, 'center_changed', tracking);
        tracking();
    };
    
    // target의 추적을 중지합니다.
    this.stop = function() {
        kakao.maps.event.removeListener(map, 'zoom_start', hideTracker);
        kakao.maps.event.removeListener(map, 'zoom_changed', tracking);
        kakao.maps.event.removeListener(map, 'center_changed', tracking);
        setVisible(false);
    };
}

// 툴팁 마커 끝

// 집중 관찰 환자 위치 불러오기
function getFocusLocation(props){
	
	// 환자 위치 저장 딕셔너리
	var position = {};
	
	// 마커 삭제
	let trackerElements = document.querySelectorAll('.tracker');
	console.log(trackerElements);
	for(let i = 0; i < markers.length; i++){
		markers[i].setMap(null);
		
		if(trackerElements.length > 0)	{
		var trackerKill = trackerElements[i];
		trackerKill.parentNode.removeChild(trackerKill);
		}
	}
	
	$.getJSON("/focusToPatient/"+props.name+"/"+props.phone,function(data){
		console.log(data);
		
		//마커 옵션
		var focusedImageSize = new kakao.maps.Size(24, 35); 
		var focusedMarkerImage = new kakao.maps.MarkerImage(focusedImageSrc, focusedImageSize);
		
		position = {
				title: data[0].name,
				latlng: new kakao.maps.LatLng(data[0].x, data[0].y)
		};

		// 마커 생성 ( 지속적으로 생성되야함 )
		var focusedMarker = new kakao.maps.Marker({
	        map: map, // 마커를 표시할 지도
	        position: position.latlng, // 마커를 표시할 위치
	        title : position.title, // 마커의 타이틀, 마커에 마우스를 올리면 타이틀이 표시됩니다
	        image : focusedMarkerImage // 마커 이미지 
	    });
		
		markers.push(focusedMarker);
		
		// 맵 center 갱신
		var moveLatLon = position.latlng;
		map.panTo(moveLatLon);
	});
};

// 환자 집중 관찰 함수
function focusToPatient(event){
	console.log(event);
	
	// 기존의 마커 생성 멈춤
	clearInterval(intervalId);
	clearInterval(intervalFocus);
	
	// 특정 환자의 위치 정보 받아오는 함수 호출
	let li = event.target;
	let phone = li.dataset.key;
	let name = li.textContent;
	
	getFocusLocation({name:name,phone:phone});
	intervalFocus = setInterval(function() {
		getFocusLocation({name:name,phone:phone});
	}, 5000);
	
};


//병원에 속한 모든 환자 정보(위치) 받아오기
function makeMarkers(hospital){
	// 마커 삭제
	let trackerElements = document.querySelectorAll('.tracker');
	for(let i = 0; i < markers.length; i++){
		markers[i].setMap(null);
		
		if(trackerElements.length > 0)	{
		var trackerKill = trackerElements[i];
		trackerKill.parentNode.removeChild(trackerKill);
		}
	}
	
	markers = [];
	console.log("trackerElements : "+trackerElements);
	
	// 병원 이름을 바탕으로 환자 정보를 불러오고, 환자 정보를 바탕으로 위치 데이터를 받아와야한다.
	$.getJSON("/getLocationData/"+hospital,function(data){
		console.log(data);
		
		let markerTrackers = [];
		
		// 받아온 데이터 for 문
		for(let i = 0; i < data.length; i++){
			// 마커 좌표 생성
			let position = new kakao.maps.LatLng(data[i].x,data[i].y);
			
			// TooltipMarker 생성
			let marker = new TooltipMarker(position, data[i].name);
            marker.setMap(map);
			markers.push(marker);
			
			console.log("marker:"+marker);
            
			// MarkerTracker 생성
			var markerTracker = new MarkerTracker(map, marker);
			markerTrackers.push(markerTracker);
			
            
		}
		
		for(let i = 0; i < markerTrackers.length; i++){
			markerTrackers[i].run();
		}
		
		console.log(markers);
		console.log(markerTrackers);
		
	})
}

const hospitalNameBox = document.getElementById('hospitalNameBox');
// 병원의 환자 정보(리스트) 받아오기
function getPatientInfo(hospital){
	hospitalNameBox.innerText = hospital;
	// 병원 이름을 바탕으로 환자 정보를 불러오고, 환자 정보를 바탕으로 위치 데이터를 받아와야한다.
	$.getJSON("/getPatientsData/"+hospital,function(data){
		console.log(data);
		
		let str = "";
		
		// 받아온 데이터 for 문
		for(let i = 0; i < data.length; i++){
			// 환자 리스트 생성
			str+="<li class='patientName' data-key='"+data[i].phone+"'>"+data[i].name+"</li>"
		}
		
		$("#customerListUl").html(str);
		
		$(document).on("click",".patientName",focusToPatient);
		
	})
	
	intervalId = setInterval(function() {
		makeMarkers(hospital);
	}, 5000);
	
}

// 포커싱 리셋 버튼
const focusResetBtn = document.getElementById('focusResetBtn');
focusResetBtn.addEventListener('click',function(){
	let hospital = hospitalNameBox.innerText;
	clearInterval(intervalFocus);
	clearInterval(intervalId);
	
	makeMarkers(hospital);
	intervalId = setInterval(function() {
		makeMarkers(hospital);
	}, 5000);
})

// 병원 정보 받아오기
function getHospitalInfo(hospital){ // props를 받을 것
	
	// 병원의 x, y 좌표를 얻어올 것.
	
	/* let newCenter = new kakao.maps.LatLng(lat, lng);
	 * map.setCenter() 병원의 좌표를 설정해서 맵의 중심을 변경해주자*/
	
	/*map은 모든 css가 변경되고 나서 호출되어야 정확한 크기를 나타낼 수 있다.
	위에서 disnone 같은 css의 변경이 끝났다면, 아래의 메소드로 다시 한번 map을 갱신해줘야한다.*/
	map.relayout();
	
	getPatientInfo(hospital); // 병원의 이름 넘겨주기
}

// 병원 정보 입력 버튼 클릭 시 환자 정보 나타내기 ( 임시 )
	const hospitalCheckBtn = document.getElementById('hospital-check-btn');
	
	hospitalCheckBtn.addEventListener('click',function(){
		let initDisnones = document.querySelectorAll('.initial-disnone');
		let hospitalCheckBox = document.querySelector('#hospital-check');
		let hospital = document.getElementById('hospital').value;
		
		for (let i = 0; i < initDisnones.length; i++){
			initDisnones[i].classList.remove('initial-disnone');
		}
		
		if (hospitalCheckBox){
			hospitalCheckBox.classList.add('disnone');
		}
		
			getHospitalInfo(hospital); // 병원에 대한 정보 입력 ex) 병원이름
			makeMarkers(hospital); // 5초 인터벌 없이 마커 생성
		
	})
	
var map = new kakao.maps.Map(container, options); //지도 생성 및 객체 리턴
	
	

	