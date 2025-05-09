from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TypeVar, Generic, Type

T = TypeVar('T')

@dataclass
class ApiResponse:
    """기본 API 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApiResponse':
        """딕셔너리에서 응답 객체 생성"""
        return cls(
            success=data.get('success', False),
            message=data.get('message', ''),
            data=data.get('data')
        )

@dataclass
class PaginatedResponse(Generic[T]):
    """페이지네이션된 API 응답 모델"""
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_class: Type[T]) -> 'PaginatedResponse[T]':
        """딕셔너리에서 페이지네이션 응답 객체 생성"""
        items_data = data.get('items', [])
        items = [item_class.from_dict(item) for item in items_data]
        
        return cls(
            items=items,
            total=data.get('total', 0),
            page=data.get('page', 1),
            page_size=data.get('page_size', len(items))
        )

@dataclass
class ErrorResponse:
    """API 에러 응답 모델"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorResponse':
        """딕셔너리에서 에러 응답 객체 생성"""
        return cls(
            error_code=data.get('error_code', 'unknown_error'),
            error_message=data.get('error_message', '알 수 없는 오류가 발생했습니다.'),
            details=data.get('details')
        ) 