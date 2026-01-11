using Core.Services.Abstract;
using Microsoft.EntityFrameworkCore;

namespace Infra.Repositories
{
    public class Repository<TEntity> 
    : IRepository<TEntity> 
    where TEntity : class
    {
        protected readonly DbContext _db;
        public Repository(DbContext db)
        {
            _db = db;
        }

        public void Add(TEntity entity)
        {
            _db.Set<TEntity>().Add(entity);
        }

        public void Remove(TEntity entity)
        {
            _db.Set<TEntity>().Remove(entity);
        }

        public void Update(TEntity entity)
        {
            _db.Set<TEntity>().Update(entity);
        }
        

    }
}