using AutoMapper;
using Core.DTOs;
using Core.Entities;


namespace Application.Mappers
{
    public class UserMappers: Profile
    {
        public UserMappers()
        {
            CreateMap<User, UsersDTO>();
        }
        
    }
}