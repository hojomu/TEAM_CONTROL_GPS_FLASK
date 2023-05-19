
$(function() {
    if (navigator.geolocation) {
      const saveLocation = function(latitude, longitude) {
        // 사용자 이름과 핸드폰 번호 가져오기
          const name = $('#name').val();
          const phone = $('#phone').val();
          
        // AJAX 요청을 통해 서버에 데이터 전송
        $.ajax({
          url: '/Geolocation', // 서버의 저장 로직을 처리하는 엔드포인트 URL
          method: 'POST',
          data: {
            name: name,
            phone: phone,
            x: latitude,
            y: longitude
     
          },
          success: function(response) {
            console.log('위치 정보가 성공적으로 저장되었습니다.');
          },
          error: function(xhr, status, error) {
            console.error('위치 정보 저장 중 오류가 발생했습니다:', error);
          }
        });
      };
  
      const getPosition = function() {
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            const currentCoords = {
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude
            };
  
            $('#x').html(currentCoords.latitude);  // 위도 
            $('#y').html(currentCoords.longitude); // 경도 
  
            // 서버에 위치 정보 저장 요청
            saveLocation(currentCoords.latitude, currentCoords.longitude);
          },
          function(error) {
            // 오류 처리
            switch (error.code) {
              case error.PERMISSION_DENIED:
                alert("위치 정보 사용 권한이 거부되었습니다.");
                break;
              case error.POSITION_UNAVAILABLE:
                alert("위치 정보를 사용할 수 없습니다.");
                break;
              case error.TIMEOUT:
                alert("위치 정보 요청 시간이 초과되었습니다.");
                break;
              case error.UNKNOWN_ERROR:
                alert("알 수 없는 오류가 발생하였습니다.");
                break;
            }
          },
          {
           timeout: 3000 , // 3초 내에 위치 정보 요청
           enableHighAccuracy: true // 높은 정확도 요청
          }
        );
      };
  
      let interval;
  
      $('#btnStart').click(function() {
        getPosition();
        interval = setInterval(getPosition, 1000); // 1초에 한번 씩 위치 정보 전달
      }); 
  
      $('#btnStop').click(function() {
        clearInterval(interval);
      });
  
    } else {
      alert("이 브라우저에서는 Geolocation이 지원되지 않습니다.");
    }
  });
  