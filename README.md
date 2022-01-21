# Account Book
Django 프레임워크로 만든 지출 내역을 관리할 수 있는 간단한 가계부 API이다.

## Features
- 회원가입 (이메일 + 비밀번호)
- 로그인 (이메일 + 비밀번호)
- 가계부 지출내역(금액, 메모) 남기기
- 가계부 지출내역 수정하기
- 가계부 지출내역 삭제하기
- 가계부 삭제내역 복원하기
- 가계부 지출내역 리스트 보기
- 가계부 지출내역 상세보기

## Language & Framework
- Python 3.9
- Django 3.2.10
- mysql 5.7 (DDL 파일은 8.0버전으로 되어 있으나 연동 RDS는 5.7버전으로 운영됨)

## Summary
RESTful하게 구현하였다. 로그인 시 Authorization header로 사용할 수 있는 token을 발급한다. 
가계부 관련 기능은 로그인(유효한 token을 보유한) 유저에 한하여 접근 가능하며 타인이 생성한 
지출내역에 대한 조회･수정･삭제 기능을 수행할 수 없다.

삭제된 내역은 삭제 전용 테이블을 분리하여 관리하는 방식으로 채택하였다. `is_deleted`와 같은 
플래그를 활용한 논리적 삭제로 구현하면 구현이 쉬운 장점이 있다. 하지만 가계부라는 서비스의 
특성상 삭제된 데이터를 조회하기 보단 일별 합계, 기간 합계 등을 위하여 활성화된 데이터를 
조회하는 경우가 빈번할 것이라 생각하였다. 따라서 쿼리를 줄여 DB의 부담을 줄이기 위하여 
테이블을 분리하였다.

## Installation
프로젝트를 시작하려면 도커가 설치된 환경에서 다음 커맨드를 실행. 
```bash
docker pull sh007jeong/accountbooks
docker run -d --name {custom name} -p 8000:8000 sh007jeong/accountbooks:0.2.0
```

## Use & API Document
자세한 사용방법은 아래의 API 문서에서 확인.
- [API Document](https://documenter.getpostman.com/view/13282746/UVXonEKb)