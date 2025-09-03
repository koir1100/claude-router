
# 💠 데이터클래스 값 출력을 위한 데코레이터
import dataclasses
from functools import wraps


def print_dataclass_values(cls):
    """데이터클래스의 __init__을 감싸서 인스턴스 생성 시 값을 출력하는 데코레이터"""

    # @dataclasses.dataclass가 생성한 __init__ 메서드를 가져옴
    original_init = cls.__init__

    # functools.wraps를 사용하여 원래 함수의 메타데이터를 보존
    @wraps(original_init)
    def wrapper_init(self, *args, **kwargs):
        # 1. 원래 __init__을 호출하여 인스턴스를 정상적으로 초기화
        original_init(self, *args, **kwargs)
        
        # 2. 초기화 직후, 인스턴스의 값들을 출력
        # dataclasses.asdict를 사용하면 깔끔한 딕셔너리로 변환 가능
        print(dataclasses.asdict(self))

    # 클래스의 __init__ 메서드를 우리가 만든 래퍼 함수로 교체
    cls.__init__ = wrapper_init
    
    # 수정된 클래스를 반환
    return cls