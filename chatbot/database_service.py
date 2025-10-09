"""
Database service for AI chatbot to query OMS data
"""

from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# Import all OMS models
from c2.models import (
    C2Facility, C2TechActivities, C2TechActivityImage, 
    C2User, C2Standard, C2RecentImage
)
from danao.models import (
    DanaoFacility, DanaoTechActivities, DanaoTechActivityImage,
    DanaoUser, DanaoStandard, DanaoRecentImage
)
from mindanao.models import (
    MindanaoFacility, MindanaoTechActivities, MindanaoTechActivityImage,
    MindanaoUser, MindanaoStandard, MindanaoRecentImage
)


class OMSDatabaseService:
    """Service class for querying OMS database data"""
    
    def __init__(self):
        self.region_models = {
            'C2': {
                'facility': C2Facility,
                'tech_activities': C2TechActivities,
                'tech_images': C2TechActivityImage,
                'user': C2User,
                'standard': C2Standard,
                'recent_image': C2RecentImage
            },
            'Danao': {
                'facility': DanaoFacility,
                'tech_activities': DanaoTechActivities,
                'tech_images': DanaoTechActivityImage,
                'user': DanaoUser,
                'standard': DanaoStandard,
                'recent_image': DanaoRecentImage
            },
            'Mindanao': {
                'facility': MindanaoFacility,
                'tech_activities': MindanaoTechActivities,
                'tech_images': MindanaoTechActivityImage,
                'user': MindanaoUser,
                'standard': MindanaoStandard,
                'recent_image': MindanaoRecentImage
            }
        }
    
    def get_user_region(self, user_groups: List[str]) -> str:
        """Determine user's region based on groups"""
        if any('_D' in group for group in user_groups):
            return 'Danao'
        elif any('_M' in group for group in user_groups):
            return 'Mindanao'
        else:
            return 'C2'
    
    def get_facilities_summary(self, region: str = None, user_groups: List[str] = None) -> Dict[str, Any]:
        """Get facilities summary data"""
        if region is None:
            region = self.get_user_region(user_groups or [])
        
        facility_model = self.region_models[region]['facility']
        
        try:
            facilities = facility_model.objects.all()
            
            summary = {
                'total_facilities': facilities.count(),
                'facilities_with_qr': facilities.exclude(qr_code__isnull=True).count(),
                'facilities_without_qr': facilities.filter(qr_code__isnull=True).count(),
                'recent_facilities': facilities.filter(
                    created__gte=timezone.now() - timedelta(days=30)
                ).count(),
                'facility_list': [
                    {
                        'id': f.id,
                        'name': f.name,
                        'has_qr': bool(f.qr_code),
                        'created': f.created.strftime('%Y-%m-%d') if f.created else None,
                        'updated': f.updated.strftime('%Y-%m-%d') if f.updated else None
                    }
                    for f in facilities[:10]  # Limit to 10 for response size
                ]
            }
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to get facilities data: {str(e)}'}
    
    def get_tech_activities_summary(self, region: str = None, user_groups: List[str] = None, user_id: int = None) -> Dict[str, Any]:
        """Get technical activities summary data"""
        if region is None:
            region = self.get_user_region(user_groups or [])
        
        tech_model = self.region_models[region]['tech_activities']
        
        try:
            activities = tech_model.objects.all()
            
            # Filter by user if provided and user is not AM/EV
            if user_id and user_groups:
                if not any(group in ['AM', 'EV', 'AM_D', 'EV_D', 'AM_M', 'EV_M'] for group in user_groups):
                    activities = activities.filter(uploaded_by__name_id=user_id)
            
            # Get risk distribution
            risk_distribution = {}
            for risk_type, _ in tech_model.RISK_CHOICES:
                count = activities.filter(potential_risk=risk_type).count()
                if count > 0:
                    risk_distribution[risk_type.replace('_', ' ').title()] = count
            
            # Get priority distribution
            priority_distribution = {}
            for priority, _ in tech_model.PRIORITY_CHOICES:
                count = activities.filter(levels_of_priority=priority).count()
                if count > 0:
                    priority_distribution[priority.upper()] = count
            
            summary = {
                'total_activities': activities.count(),
                'activities_this_month': activities.filter(
                    created__gte=timezone.now() - timedelta(days=30)
                ).count(),
                'activities_this_week': activities.filter(
                    created__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'pending_remarks': activities.filter(remarks__isnull=True).count(),
                'risk_distribution': risk_distribution,
                'priority_distribution': priority_distribution,
                'recent_activities': [
                    {
                        'id': a.id,
                        'name': a.name,
                        'location': a.location,
                        'uploaded_by': str(a.uploaded_by),
                        'risk': a.potential_risk,
                        'priority': a.levels_of_priority,
                        'has_remarks': bool(a.remarks),
                        'created': a.created.strftime('%Y-%m-%d %H:%M'),
                        'images_count': a.images.count() if hasattr(a, 'images') else 0
                    }
                    for a in activities[:10]  # Limit to 10
                ]
            }
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to get tech activities data: {str(e)}'}
    
    def get_user_activities(self, user_id: int, region: str = None) -> Dict[str, Any]:
        """Get activities uploaded by specific user"""
        if region is None:
            return {'error': 'Region required for user activities'}
        
        tech_model = self.region_models[region]['tech_activities']
        
        try:
            activities = tech_model.objects.filter(uploaded_by__name_id=user_id)
            
            summary = {
                'user_total_activities': activities.count(),
                'user_activities_this_month': activities.filter(
                    created__gte=timezone.now() - timedelta(days=30)
                ).count(),
                'user_recent_activities': [
                    {
                        'id': a.id,
                        'name': a.name,
                        'location': a.location,
                        'risk': a.potential_risk,
                        'priority': a.levels_of_priority,
                        'created': a.created.strftime('%Y-%m-%d'),
                        'images_count': a.images.count() if hasattr(a, 'images') else 0
                    }
                    for a in activities[:5]  # Limit to 5
                ]
            }
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to get user activities: {str(e)}'}
    
    def get_facility_details(self, facility_id: int, region: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific facility"""
        if region is None:
            return {'error': 'Region required for facility details'}
        
        facility_model = self.region_models[region]['facility']
        
        try:
            facility = facility_model.objects.get(id=facility_id)
            
            # Get related data
            standards = facility.standards.all() if hasattr(facility, 'standards') else []
            recent_images = []
            
            # Get recent images if they exist
            if hasattr(facility, 'standards'):
                for standard in standards:
                    recent_images.extend(standard.c2recentimage_set.all())
            
            details = {
                'facility': {
                    'id': facility.id,
                    'name': facility.name,
                    'has_qr': bool(facility.qr_code),
                    'qr_url': facility.get_qr_url() if hasattr(facility, 'get_qr_url') else None,
                    'created': facility.created.strftime('%Y-%m-%d') if facility.created else None,
                    'updated': facility.updated.strftime('%Y-%m-%d') if facility.updated else None
                },
                'standards_count': len(standards),
                'recent_images_count': len(recent_images),
                'latest_standard': {
                    'updated': standards[0].updated.strftime('%Y-%m-%d') if standards else None
                } if standards else None
            }
            
            return details
            
        except facility_model.DoesNotExist:
            return {'error': f'Facility with ID {facility_id} not found'}
        except Exception as e:
            return {'error': f'Failed to get facility details: {str(e)}'}
    
    def get_activity_details(self, activity_id: int, region: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific technical activity"""
        if region is None:
            return {'error': 'Region required for activity details'}
        
        tech_model = self.region_models[region]['tech_activities']
        image_model = self.region_models[region]['tech_images']
        
        try:
            activity = tech_model.objects.get(id=activity_id)
            images = image_model.objects.filter(activity=activity)
            
            details = {
                'activity': {
                    'id': activity.id,
                    'name': activity.name,
                    'location': activity.location,
                    'uploaded_by': str(activity.uploaded_by),
                    'remarks': activity.remarks,
                    'potential_risk': activity.potential_risk,
                    'probability': activity.probability_of_occurrence,
                    'impact': activity.impact,
                    'priority': activity.levels_of_priority,
                    'created': activity.created.strftime('%Y-%m-%d %H:%M'),
                    'updated': activity.updated.strftime('%Y-%m-%d %H:%M')
                },
                'images_count': images.count(),
                'images': [
                    {
                        'id': img.id,
                        'label': img.label,
                        'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M')
                    }
                    for img in images[:5]  # Limit to 5 images
                ]
            }
            
            return details
            
        except tech_model.DoesNotExist:
            return {'error': f'Activity with ID {activity_id} not found'}
        except Exception as e:
            return {'error': f'Failed to get activity details: {str(e)}'}
    
    def search_facilities(self, search_term: str, region: str = None, user_groups: List[str] = None) -> Dict[str, Any]:
        """Search facilities by name"""
        if region is None:
            region = self.get_user_region(user_groups or [])
        
        facility_model = self.region_models[region]['facility']
        
        try:
            facilities = facility_model.objects.filter(
                name__icontains=search_term
            )[:10]  # Limit results
            
            results = {
                'search_term': search_term,
                'total_found': facilities.count(),
                'facilities': [
                    {
                        'id': f.id,
                        'name': f.name,
                        'has_qr': bool(f.qr_code),
                        'created': f.created.strftime('%Y-%m-%d') if f.created else None
                    }
                    for f in facilities
                ]
            }
            
            return results
            
        except Exception as e:
            return {'error': f'Failed to search facilities: {str(e)}'}
    
    def search_activities(self, search_term: str, region: str = None, user_id: int = None) -> Dict[str, Any]:
        """Search technical activities by name or location"""
        if region is None:
            return {'error': 'Region required for activity search'}
        
        tech_model = self.region_models[region]['tech_activities']
        
        try:
            activities = tech_model.objects.filter(
                Q(name__icontains=search_term) | Q(location__icontains=search_term)
            )
            
            # Filter by user if provided
            if user_id:
                activities = activities.filter(uploaded_by__name_id=user_id)
            
            activities = activities[:10]  # Limit results
            
            results = {
                'search_term': search_term,
                'total_found': activities.count(),
                'activities': [
                    {
                        'id': a.id,
                        'name': a.name,
                        'location': a.location,
                        'uploaded_by': str(a.uploaded_by),
                        'risk': a.potential_risk,
                        'priority': a.levels_of_priority,
                        'created': a.created.strftime('%Y-%m-%d'),
                        'images_count': a.images.count() if hasattr(a, 'images') else 0
                    }
                    for a in activities
                ]
            }
            
            return results
            
        except Exception as e:
            return {'error': f'Failed to search activities: {str(e)}'}
    
    def get_statistics(self, region: str = None, user_groups: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive OMS statistics"""
        if region is None:
            region = self.get_user_region(user_groups or [])
        
        try:
            facility_model = self.region_models[region]['facility']
            tech_model = self.region_models[region]['tech_activities']
            
            # Facility stats
            total_facilities = facility_model.objects.count()
            facilities_with_qr = facility_model.objects.exclude(qr_code__isnull=True).count()
            
            # Activity stats
            total_activities = tech_model.objects.count()
            activities_this_month = tech_model.objects.filter(
                created__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            # Risk stats
            high_risk_activities = tech_model.objects.filter(
                potential_risk__in=['operational', 'environmental', 'employee']
            ).count()
            
            # Priority stats
            critical_activities = tech_model.objects.filter(
                levels_of_priority__in=['p1', 'p2']
            ).count()
            
            stats = {
                'region': region,
                'facilities': {
                    'total': total_facilities,
                    'with_qr_codes': facilities_with_qr,
                    'without_qr_codes': total_facilities - facilities_with_qr,
                    'qr_coverage_percentage': round((facilities_with_qr / total_facilities * 100), 1) if total_facilities > 0 else 0
                },
                'activities': {
                    'total': total_activities,
                    'this_month': activities_this_month,
                    'high_risk': high_risk_activities,
                    'critical_priority': critical_activities
                },
                'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return stats
            
        except Exception as e:
            return {'error': f'Failed to get statistics: {str(e)}'}


# Global instance
db_service = OMSDatabaseService()
