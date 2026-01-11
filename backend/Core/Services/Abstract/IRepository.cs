
namespace Core.Services.Abstract
{
    public interface IRepository<TEntity> 
    where TEntity : class
    {
        public void Add(TEntity entity);
        public void Remove(TEntity entity);
        public void Update(TEntity entity); 
    }
}